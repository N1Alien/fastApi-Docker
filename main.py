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

# --- 2. POBRANIE CONFIGU GOOGLE GEMINI ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI(title="Stabilny i Darmowy RAG w Chmurze", version="1.0.0", redirect_slashes=True)

class PytanieRequest(BaseModel):
    prompt: str

# --- 3. GENERATOR ASYNCHRONICZNY (RAG + GEMINI STREAM) ---
async def gemini_rag_generator(prompt: str):
    try:
        # Krok A: Pobranie wiedzy z bazy danych pgvector z wczoraj
        session = SessionLocal()
        wynik_bazy = session.execute(text("SELECT content FROM documents LIMIT 1;")).fetchone()
        session.close()
        
        kontekst = wynik_bazy[0] if wynik_bazy else "Brak dodatkowego kontekstu w bazie danych."
        
        # Krok B: Przygotowanie ustrukturyzowanego zapytania dla Google Gemini
        instrukcja_systemowa = f"Jesteś pomocnym asystentem RAG. Odpowiadaj wyłącznie na podstawie podanego kontekstu: {kontekst}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{instrukcja_systemowa}\n\nPytanie użytkownika: {prompt}"}
                    ]
                }
            ]
        }
        
        # Oficjalny endpoint Google Gemini obsługujący asynchroniczne strumieniowanie (Server-Sent Events)
        API_URL = f"https://googleapis.com{GEMINI_API_KEY}"

        # Krok C: Przesyłanie strumienia danych token po tokenie
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", API_URL, json=payload) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    yield f"\n[Błąd Gemini API (Status {response.status_code}): {error_text.decode('utf-8')}]"
                    return
                
                # Google Gemini zwraca strumień bloków tekstowych w formacie JSON
                async for chunk in response.aiter_text():
                    if chunk:
                        try:
                            # Oczyszczamy i parsujemy napływającą strukturę danych od Google
                            cleaned_chunk = chunk.strip().lstrip(',').rstrip(',')
                            if cleaned_chunk.startswith('[') or cleaned_chunk.endswith(']'):
                                continue
                                
                            chunk_json = json.loads(cleaned_chunk)
                            token = chunk_json["candidates"][0]["content"]["parts"][0]["text"]
                            if token:
                                yield token
                        except Exception:
                            # Czasami stream wysyła metadane systemowe, ignorujemy błędy parsowania pojedynczych linii
                            continue

    except Exception as e:
        yield f"\n[Błąd systemu RAG: {str(e)}]"

# --- 4. ENDPOINT PUBLICZNY ---
@app.post("/rag-hf-stream")
async def rag_hf_stream(dane: PytanieRequest):
    """W 100% stabilny, darmowy stream RAG oparty o Google Gemini API."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Brakuje zmiennej środowiskowej GEMINI_API_KEY w panelu Render.")
        
    return StreamingResponse(
        gemini_rag_generator(prompt=dane.prompt),
        media_type="text/plain; charset=utf-8"
    )
