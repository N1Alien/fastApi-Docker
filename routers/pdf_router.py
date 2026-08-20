# Folder: routers/ | Plik: pdf_router.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import text
from services.auth_service import get_current_user_id
from services.pdf_service import extract_and_chunk_pdf, generate_vector_embedding

router = APIRouter(tags=["3. Knowledge Base Ingestion"])

@router.post("/upload-pdf", summary="Upload and vectorize a private corporate PDF document")
async def upload_pdf(file: UploadFile = File(...), current_user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    try:
        file_bytes = await file.read()
        chunks = extract_and_chunk_pdf(file_bytes)
        if not chunks:
            raise HTTPException(status_code=400, detail="Could not read text from this PDF file.")
            
        # TYMCZASOWA POPRAWKA: Kasujemy stary, niekompatybilny worek na dokumenty
        db.execute(text("DROP TABLE IF EXISTS ollama_documents;"))
        db.commit()
        
        # Tworzymy tabelę od zera z poprawną kolumną user_id
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS ollama_documents (
                id SERIAL PRIMARY KEY, 
                user_id TEXT NOT NULL, 
                content TEXT NOT NULL, 
                embedding vector(768)
            );
        """))
        db.commit()
        
        for chunk in chunks:
            vector_values = generate_vector_embedding(chunk)
            db.execute(text("INSERT INTO ollama_documents (user_id, content, embedding) VALUES (:user_id, :content, CAST(:embedding AS vector))"), {"user_id": current_user_id, "content": chunk, "embedding": str(vector_values)})
        db.commit()
        return {"status": "success", "indexed_chunks": len(chunks), "file_name": file.filename}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")
