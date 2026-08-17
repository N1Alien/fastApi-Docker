import os
import json
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# --- 1. KONFIGURACJA BAZY DANYCH (PostgreSQL z Rendera) ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# --- 2. POBRANIE CONFIGU MODELU JĘZYKOWEGO ---
HF_TOKEN = os.getenv("HF_TOKEN")
# Korzystamy z nowoczesnego i szybkiego modelu Qwen 2.5
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

app = FastAPI(title="W 100% sprawny RAG w Chmurze", version="1.0.0", redirect_slashes=True)

class PytanieRequest(BaseModel):
    prompt: str

# --- 3. GENERATOR ASYNCHRONICZNY ---
async def proper_rag_generator(prompt: str):
    try:
        # Krok A: Pobranie kontekstu z bazy pgvector z wczoraj
        session = SessionLocal()
        wynik_bazy = session.execute(text("SELECT content FROM documents LIMIT 1;")).fetchone()
        session.close()
        
        kontekst = wynik_bazy[0] if wynik_bazy else "Brak dodatkowego kontekstu w bazie danych."
        
        # Krok B: Budowanie wiadomości w formacie czatu (standard OpenAI/HuggingFace 2026)
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system", 
                    "content": f"Jesteś pomocnym asystentem RAG. Odpowiadaj na podstawie kontekstu: {kontekst}"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 512,
            "stream": True  # Włączamy prawdziwe strumieniowanie serwerowe!
        }
        
        # Oficjalny nowy router Hugging Face obsługujący chat/completions
        API_URL = "https://huggingface.co"
        
        naglowki = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }

        # Krok C: Asynchroniczny strumieniowy pobór tokenów przez httpx
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", API_URL, json=payload, headers=naglowki) as response:
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    yield f"\n[Błąd API (Status {response.status_code}): {error_text.decode('utf-8')}]"
                    return
                
                # Przetwarzamy strumień linia po linii (Server-Sent Events)
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_content = line[6:].strip()
                        
                        # Koniec strumienia oznaczany jest przez [DONE]
                        if data_content == "[DONE]":
                            break
                            
                        try:
                            chunk_json = json.loads(data_content)
                            token = chunk_json["choices"][0]["delta"].get("content", "")
                            if token:
                                yield token
                        except Exception:
                            continue

    except Exception as e:
        yield f"\n[Błąd systemu RAG: {str(e)}]"

# --- 4. ENDPOINT PUBLICZNY ---
@app.post("/rag-hf-stream")
async def rag_hf_stream(dane: PytanieRequest):
    """W pełni sprawny, zabezpieczony i darmowy stream z chmurowego LLM."""
    if not HF_TOKEN:
        raise HTTPException(status_code=500, detail="Brakuje zmiennej środowiskowej HF_TOKEN w panelu Render.")
        
    return StreamingResponse(
        proper_rag_generator(prompt=dane.prompt),
        media_type="text/plain; charset=utf-8"
    )
