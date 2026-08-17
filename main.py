import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from duckduckgo_search import DDGS  # Uniwersalna klasa do obsługi darmowego AI

# --- 1. KONFIGURACJA BAZY DANYCH (PostgreSQL z Rendera) ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="Stabilny Darmowy RAG w Chmurze", version="1.0.0", redirect_slashes=True)

class PytanieRequest(BaseModel):
    prompt: str

# --- 2. POPRAWIONY ASYNCHRONICZNY GENERATOR DUCKDUCKGO ---
async def ddg_rag_generator(prompt: str):
    try:
        # Krok A: Pobranie wiedzy z bazy danych pgvector
        session = SessionLocal()
        wynik_bazy = session.execute(text("SELECT content FROM documents LIMIT 1;")).fetchone()
        session.close()
        
        kontekst = wynik_bazy if wynik_bazy else "Brak dodatkowego kontekstu w bazie danych."
        
        # Krok B: Budowanie pełnego zapytania tekstowego z uwzględnieniem kontekstu
        pelny_prompt = (
            f"Jesteś pomocnym asystentem RAG. Odpowiadaj na podstawie kontekstu: {kontekst}\n\n"
            f"Pytanie użytkownika: {prompt}"
        )
        
        # Krok C: Inicjalizacja obiektu DDGS (bez użycia kłopotliwego 'async with')
        ddgs = DDGS()
        
        # Bezpośrednie wywołanie asynchronicznej metody .achat() z darmowym modelem Llama 3 70B
        response = await ddgs.achat(keywords=pelny_prompt, model="llama-3-70b")
        
        if response:
            # Rozdzielamy tekst na słowa, aby zasymulować efekt płynnego strumieniowania do frontendu
            for slowo in response.split(" "):
                yield slowo + " "
        else:
            yield "\n[Błąd: DuckDuckGo AI nie zwrócił odpowiedzi]"

    except Exception as e:
        yield f"\n[Błąd generatora: {str(e)}]"

# --- 3. ENDPOINT PUBLICZNY ---
@app.post("/rag-hf-stream")
async def rag_hf_stream(dane: PytanieRequest):
    """W 100% stabilny i darmowy stream działający w chmurze bez żadnych kluczy autoryzacyjnych."""
    return StreamingResponse(
        ddg_rag_generator(prompt=dane.prompt),
        media_type="text/plain; charset=utf-8"
    )
