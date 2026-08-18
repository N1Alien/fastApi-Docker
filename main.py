import os
import io
import json
import urllib.request
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

# --- 2. EMBEDDED OLLAMA CONFIGURATION (FOR EMBEDDINGS ONLY) ---
ollama_client = ollama.Client(host="http://127.0.0.1:11434")

app = FastAPI(title="Hybrid Free Cloud RAG Container", version="3.2.0", redirect_slashes=True)

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

# --- 4. RAG GENERATOR VIA FREE WEB API ---
async def smart_rag_generator(prompt: str):
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
        
        context = "\n---\n".join([row[0] for row in db_results]) if db_results else "No matching documents found."
        
        # Przygotowanie zapytania dla darmowego, zewnętrznego modelu Qwen (odporne na limity pamięci RAM)
        full_prompt = (
            f"<|im_start|>system\nAnswer based on this PDF context: {context}<|im_end|>\n"
            f"<|im_start|>user\n{prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        
        API_URL = "https://huggingface.co"
        payload = {
            "inputs": full_prompt,
            "parameters": {"max_new_tokens": 512, "return_full_text": False}
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(API_URL, data=data, headers={"Content-Type": "application/json"})
        
        with urllib.request.urlopen(req, timeout=30) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            if isinstance(res_body, list) and len(res_body) > 0:
                generated_text = res_body[0].get("generated_text", "")
            else:
                generated_text = str(res_body)
                
            generated_text = generated_text.replace("<|im_end|>", "").strip()
            
            for word in generated_text.split(" "):
                yield word + " "

    except Exception as e:
        yield f"\n[Cloud RAG Error: {str(e)}]"

# --- 5. ENDPOINT: CHAT WITH MODEL ---
@app.post("/chat-with-model")
async def chat_with_model(request_data: ChatRequest):
    return StreamingResponse(
        smart_rag_generator(prompt=request_data.prompt),
        media_type="text/plain; charset=utf-8"
    )
