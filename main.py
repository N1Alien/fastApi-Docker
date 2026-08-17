import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from huggingface_hub import AsyncInferenceClient

# 1. Baza danych z Rendera
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# 2. Klient Hugging Face (token z ustawień profilu)
HF_TOKEN = os.getenv("HF_TOKEN")
# Używamy popularnego, darmowego modelu hostowanego na serverless API Hugging Face
HF_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
hf_client = AsyncInferenceClient(model=HF_MODEL, token=HF_TOKEN)

app = FastAPI(title="Hugging Face RAG Stream w Chmurze", version="1.0.0", redirect_slashes=True)

class PytanieRequest(BaseModel):
    prompt: str

async def hf_rag_generator(prompt: str):
    """Pobiera kontekst z pgvector i strumieniuje tekst z Hugging Face."""
    try:
        session = SessionLocal()
        wynik_bazy = session.execute(text("SELECT content FROM documents LIMIT 1;")).fetchone()
        session.close()
        
        kontekst = wynik_bazy if wynik_bazy else "Brak dodatkowego kontekstu."
        
        pelny_prompt = f"Kontekst: {kontekst}\n\nPytanie: {prompt}"

        # Asynchroniczne strumieniowanie z Hugging Face Serverless API
        stream = await hf_client.text_generation(
            prompt=pelny_prompt,
            stream=True,
            max_new_tokens=512
        )
        
        async for chunk in stream:
            yield chunk

    except Exception as e:
        yield f"\n[Błąd Hugging Face: {str(e)}]"

@app.post("/rag-hf-stream")
async def rag_hf_stream(dane: PytanieRequest):
    if not HF_TOKEN:
        raise HTTPException(status_code=500, detail="Brak zmiennej środowiskowej HF_TOKEN.")
        
    return StreamingResponse(
        hf_rag_generator(prompt=dane.prompt),
        media_type="text/plain; charset=utf-8"
    )
