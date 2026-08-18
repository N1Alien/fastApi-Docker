import os
import io
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import ollama
from pypdf import PdfReader
from google import genai
from google.genai import types

# --- 1. DATABASE CONFIGURATION ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# --- 2. GOOGLE GENAI & EMBEDDED OLLAMA CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Inicjalizacja nowoczesnego klienta Google GenAI (będzie generował czat)
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else genai.Client()

# Inicjalizacja klienta Ollama (generuje wyłącznie wektory 768 w tle)
ollama_client = ollama.Client(host="http://127.0.0.1:11434")

app = FastAPI(title="Hybrid Free Cloud RAG Container", version="3.4.0", redirect_slashes=True)

class ChatRequest(BaseModel):
    prompt: str

def split_text(text_content: str, chunk_size: int = 400, overlap: int = 50):
    chunks = []
    start = 0
    text_length = len(text_content)
    while start < text_length:
        end = start + chunk_size
        chunks.append(text_content[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]

# --- 3. ENDPOINT: UPLOAD PDF ---
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
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
                CREATE TABLE IF NOT EXISTS ollama_documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector(768)
                );
            """))
            
            for chunk in chunks:
                embed_res = ollama_client.embeddings(
                    model='nomic-embed-text',
                    prompt=chunk
                )
                vector_values = embed_res['embedding']
                vector_str = str(vector_values)
                
                conn.execute(
                    text("INSERT INTO ollama_documents (content, embedding) VALUES (:content, CAST(:embedding AS vector))"),
                    {"content": chunk, "embedding": vector_str}
                )
                
        return {"status": "success", "indexed_chunks": len(chunks), "file_name": file.filename}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")

# --- 4. RAG GENERATOR VIA STABLE GOOGLE GEMINI SDK ---
async def smart_rag_generator(prompt: str):
    try:
        # Generowanie wektora zapytania o wymiarowości 768 przez wewnętrzną Ollamę
        query_embed = ollama_client.embeddings(
            model='nomic-embed-text',
            prompt=prompt
        )
        query_vector_str = str(query_embed['embedding'])
        
        session = SessionLocal()
        # Wyciągamy dane z nowej, działającej tabeli wektorowej 768
        db_results = session.execute(
            text("SELECT content FROM ollama_documents ORDER BY embedding <=> CAST(:qvec AS vector) LIMIT 6;"),
            {"qvec": query_vector_str}
        ).fetchall()
        session.close()
        
        if db_results:
            context = "\n---\n".join([row[0] for row in db_results])
        else:
            context = "No matching documents found in the database."
            
        # Generowanie odpowiedzi przy użyciu bezpiecznego klucza Gemini przez oficjalne, nowoczesne SDK
        response = client.models.generate_content(
            model='gemini-2.5-flash',
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
    """Streams responses from Gemini model enriched with local Ollama 768 vector context."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GEMINI_API_KEY in Render environment.")
        
    return StreamingResponse(
        smart_rag_generator(prompt=request_data.prompt),
        media_type="text/plain; charset=utf-8"
    )
