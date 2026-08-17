import os
import io
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from google import genai
from google.genai import types
from pypdf import PdfReader

# --- 1. DATABASE CONFIGURATION ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# --- 2. GOOGLE GENAI SDK CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else genai.Client()

app = FastAPI(title="RAG with PDF and pgvector in Cloud", version="2.9.0", redirect_slashes=True)

class ChatRequest(BaseModel):
    prompt: str

def split_text(text_content: str, chunk_size: int = 400, overlap: int = 50):
    """Simple chunking strategy with overlap."""
    chunks = []
    start = 0
    text_length = len(text_content)
    while start < text_length:
        end = start + chunk_size
        chunks.append(text_content[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]

# --- 3. ENDPOINT: UPLOAD PDF, CHUNK AND SAVE EMBEDDINGS ---
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Receives a PDF file, extracts text, splits into chunks, generates embeddings and saves to pgvector."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GEMINI_API_KEY.")
        
    try:
        pdf_bytes = await file.read()
        pdf_stream = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_stream)
        
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
                
        if not full_text.strip():
            raise HTTPException(status_code=400, detail="Could not read text from this PDF file.")
            
        chunks = split_text(full_text)
        
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector(1536)
                );
            """))
            
            for chunk in chunks:
                embed_result = client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=chunk,
                    config=types.EmbedContentConfig(output_dimensionality=1536)
                )
                vector_values = embed_result.embeddings.values
                vector_str = str(vector_values)
                
                conn.execute(
                    text("INSERT INTO documents (content, embedding) VALUES (:content, CAST(:embedding AS vector))"),
                    {"content": chunk, "embedding": vector_str}
                )
                
        return {"status": "success", "indexed_chunks": len(chunks), "file_name": file.filename}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")

# --- 4. RAG GENERATOR BUSINESS LOGIC ---
async def smart_rag_generator(prompt: str):
    """Searches for context using pgvector and generates streaming response via Gemini."""
    try:
        query_embed = client.models.embed_content(
            model="gemini-embedding-2",
            contents=prompt,
            config=types.EmbedContentConfig(output_dimensionality=1536)
        )
        query_vector_str = str(query_embed.embeddings.values)
        
        session = SessionLocal()
        # Zwiększony limit z 3 na 6, aby pobierać więcej fragmentów z bazy wektorowej
        db_results = session.execute(
            text("SELECT content FROM documents ORDER BY embedding <=> CAST(:qvec AS vector) LIMIT 6;"),
            {"qvec": query_vector_str}
        ).fetchall()
        session.close()
        
        if db_results:
            context = "\n---\n".join([row for row in db_results])
        else:
            context = "No matching documents found in the database."
            
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=(
                f"You are an intelligent assistant. You have access to the knowledge base (PDF chunks):\n'{context}'.\n\n"
                f"If the question relates to this knowledge, use it. Otherwise, answer "
                f"based on your own general knowledge.\n\n"
                f"User question: {prompt}"
            ),
        )
        
        if hasattr(response, 'text') and response.text:
            yield response.text
        else:
            yield str(response)

    except Exception as e:
        yield f"\n[Cloud RAG Error: {str(e)}]"

# --- 5. ENDPOINT: CHAT WITH MODEL ---
@app.post("/chat-with-model")
async def chat_with_model(request_data: ChatRequest):
    """Streams responses from Gemini model enriched with vector database context."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GEMINI_API_KEY in Render environment.")
        
    return StreamingResponse(
        smart_rag_generator(prompt=request_data.prompt),
        media_type="text/plain; charset=utf-8"
    )
