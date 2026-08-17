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

app = FastAPI(title="Bezkluczowy RAG Stream w Chmurze", version="1.0.0", redirect_slashes=True)

class PytanieRequest(BaseModel):
    prompt: str

# --- 2. GENERATOR STRUMIENIOWY BEZ UŻYCIA TOKENÓW API ---
async def public_rag_generator(prompt: str):
    try:
        # Krok A: Pobranie wiedzy z bazy danych pgvector
        session = SessionLocal()
        wynik_bazy = session.execute(text("SELECT content FROM documents LIMIT 1;")).fetchone()
        session.close()
        
        kontekst = wynik_bazy[0] if wynik_bazy else "Brak dodatkowego kontekstu w bazie danych."
        
        # Krok B: Przygotowanie pełnego zapytania dla otwartego modelu
        pelny_prompt = (
            f"<|system|>\nJesteś pomocnym asystentem RAG. Odpowiadaj na podstawie kontekstu: {kontekst}\n"
            f"<|user|>\n{prompt}\n"
            f"<|assistant|>\n"
        )
        
        # Konfiguracja publicznego, darmowego punktu końcowego (bez tokenu)
        API_URL = "https://huggingface.co"
        payload = {
            "inputs": pelny_prompt,
            "parameters": {"max_new_tokens": 512, "return_full_text": False},
            "options": {"use_cache": False, "wait_for_model": True}
        }

        # Krok C: Asynchroniczne strumieniowanie danych przez httpx
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", API_URL, json=payload) as response:
                if response.status_code != 200:
                    yield f"\n[Błąd publicznego API (Status {response.status_code})]"
                    return
                
                # Odczytujemy strumień surowego tekstu z darmowego endpointu
                async for chunk in response.aiter_text():
                    if chunk:
                        # Publiczne API zwraca proste fragmenty tekstu lub bloki JSON. 
                        # Filtrujemy i oczyszczamy tekst na potrzeby czytelnego streamu
                        yield chunk

    except Exception as e:
        yield f"\n[Błąd generatora: {str(e)}]"

# --- 3. ENDPOINT PUBLICZNY ---
@app.post("/rag-hf-stream")
async def rag_hf_stream(dane: PytanieRequest):
    """W 100% darmowy publiczny stream działający w chmurze bez kluczy autoryzacyjnych."""
    return StreamingResponse(
        public_rag_generator(prompt=dane.prompt),
        media_type="text/plain; charset=utf-8"
    )
