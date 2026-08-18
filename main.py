import os
import io
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import ollama
from pypdf import PdfReader

# --- 1. DATABASE CONFIGURATION ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# --- 2. EMBEDDED OLLAMA CONFIGURATION ---
# Ollama działa w tym samym kontenerze, więc uderzamy w localhost
ollama_client = ollama.Client(host="http://127.0.0.1:11434")

app = FastAPI(title="All-in-One Cloud RAG Container", version="3.1.0", redirect_slashes=True)

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
    """Receives a PDF file, extracts text, splits into chunks, generates embeddings via Ollama and saves to pgvector."""
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
            # Model nomic-embed-text z Ollamy generuje 768 wymiarów
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS documents (
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
                    text("INSERT INTO documents (content, embedding) VALUES (:content, CAST(:embedding AS vector))"),
                    {"content": chunk, "embedding": vector_str}
                )
                
        return {"status": "success", "indexed_chunks": len(chunks), "file_name": file.filename}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")

# --- 4. RAG GENERATOR BUSINESS LOGIC ---
async def smart_rag_generator(prompt: str):
    """Searches for context using pgvector and generates streaming response via local container Ollama."""
    try:
        query_embed = ollama_client.embeddings(
            model='nomic-embed-text',
            prompt=prompt
        )
        query_vector_str = str(query_embed['embedding'])
        
        session = SessionLocal()
        db_results = session.execute(
            text("SELECT content FROM documents ORDER BY embedding <=> CAST(:qvec AS vector) LIMIT 6;"),
            {"qvec": query_vector_str}
        ).fetchall()
        session.close()
        
        context = "\n---\n".join([row for row in db_results]) if db_results else "No matching documents found."
        
        # Strumieniowanie z modelu llama3.2 zainstalowanego wewnątrz kontenera
        stream = ollama_client.chat(
            model='llama3.2',
            messages=[
                {
                    'role': 'system', 
                    'content': f"You are an intelligent assistant. Answer the user based on this PDF context:\n{context}"
                },
                {'role': 'user', 'content': prompt}
            ],
            stream=True,
        )
        for chunk in stream:
            yield chunk['message']['content']

    except Exception as e:
        yield f"\n[Container Ollama Error: {str(e)}]"

# --- 5. ENDPOINT: CHAT WITH MODEL ---
@app.post("/chat-with-model")
async def chat_with_model(request_data: ChatRequest):
    """Streams responses from internal Ollama model enriched with vector database context."""
    return StreamingResponse(
        smart_rag_generator(prompt=request_data.prompt),
        media_type="text/plain; charset=utf-8"
    )
