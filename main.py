import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import google.generativeai as genai

# --- 1. wczorajsza baza danych (PostgreSQL + pgvector z Rendera) ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# --- 2. Konfiguracja oficjalnego SDK Google Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="RAG z pgvector i Gemini w Chmurze", version="1.0.0", redirect_slashes=True)

class PytanieRequest(BaseModel):
    prompt: str

async def full_rag_generator(prompt: str):
    """Pobiera realny kontekst z pgvector i strumieniuje odpowiedź z Gemini SDK."""
    try:
        # Krok A: Wczorajsze wyszukiwanie w bazie danych
        session = SessionLocal()
        wynik_bazy = session.execute(text("SELECT content FROM documents LIMIT 1;")).fetchone()
        session.close()
        
        kontekst = wynik_bazy if wynik_bazy else "Brak dodatkowego kontekstu w bazie danych."

        # Krok B: Sprawdzenie klucza i inicjalizacja modelu
        if not GEMINI_API_KEY:
            yield "[Błąd: Brak klucza GEMINI_API_KEY]"
            return

        model = genai.GenerativeModel('gemini-1.5-flash')
        
        pelny_prompt = (
            f"Jesteś pomocnym asystentem RAG. Odpowiadaj wyłącznie na podstawie poniższego kontekstu.\n\n"
            f"Kontekst z bazy danych: {kontekst}\n\n"
            f"Pytanie użytkownika: {prompt}"
        )

        # Krok C: Bezpieczne strumieniowanie przez natywne SDK Google
        response = model.generate_content(pelny_prompt, stream=True)
        
        for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        yield f"\n[Błąd generatora RAG: {str(e)}]"

@app.post("/rag-hf-stream")
async def rag_hf_stream(dane: PytanieRequest):
    """Główny endpoint łączący wczorajszą bazę pgvector z dzisiejszym stabilnym Gemini."""
    return StreamingResponse(
        full_rag_generator(prompt=dane.prompt),
        media_type="text/plain; charset=utf-8"
    )
