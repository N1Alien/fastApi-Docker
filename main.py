import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from huggingface_hub import AsyncInferenceClient

# --- 1. KONFIGURACJA BAZY DANYCH (PostgreSQL + pgvector z Rendera) ---
# Pobieramy adres URL bazy (External lub Internal) ze zmiennych środowiskowych Rendera
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# --- 2. KONFIGURACJA REPOZYTORIUM MODELI (Hugging Face Serverless) ---
# Pobieramy token autoryzacyjny ze zmiennych środowiskowych Rendera
HF_TOKEN = os.getenv("HF_TOKEN")
# Wybieramy stabilny, darmowy model Llama 3 dopasowany do zadań konwersacyjnych
HF_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
hf_client = AsyncInferenceClient(model=HF_MODEL, token=HF_TOKEN)

# Inicjalizacja aplikacji FastAPI z włączonym automatycznym przekierowaniem ukośników
app = FastAPI(title="Hugging Face RAG Stream w Chmurze", version="1.0.0", redirect_slashes=True)

# --- 3. MODELE WALIDACJI (Pydantic) ---
class PytanieRequest(BaseModel):
    prompt: str

# --- 4. GENERATOR ASYNCHRONICZNY (Logika RAG + Strumieniowanie) ---
async def hf_rag_generator(prompt: str):
    """Pobiera kontekst z pgvector i strumieniuje czat z Hugging Face."""
    try:
        # Krok A: Pobranie przykładowej wiedzy z bazy danych
        session = SessionLocal()
        wynik_bazy = session.execute(text("SELECT content FROM documents LIMIT 1;")).fetchone()
        session.close()
        
        # Jeśli baza jest pusta, używamy domyślnego tekstu pomocniczego
        kontekst = wynik_bazy[0] if wynik_bazy else "Brak dodatkowego kontekstu w bazie danych."
        
        # Krok B: Budowanie ustrukturyzowanej listy wiadomości (format conversational)
        wiadomosci = [
            {
                "role": "system", 
                "content": "Jesteś pomocnym asystentem RAG. Odpowiadaj wyłącznie na podstawie podanego kontekstu."
            },
            {
                "role": "user", 
                "content": f"Kontekst z bazy danych: {kontekst}\n\nPytanie: {prompt}"
            }
        ]

        # Krok C: Asynchroniczne odpytanie i strumieniowanie z Hugging Face Serverless API
        stream = await hf_client.chat.completions.create(
            model=HF_MODEL,
            messages=wiadomosci,
            stream=True,
            max_tokens=512
        )
        
        # Krok D: Przekazywanie napływających tokenów tekstowych bezpośrednio do klienta HTTP
        async for chunk in stream:
            token = chunk.choices.delta.content
            if token:
                yield token

    except Exception as e:
        yield f"\n[Błąd Hugging Face: {str(e)}]"

# --- 5. ENDPOINT PUBLICZNY ---
@app.post("/rag-hf-stream")
async def rag_hf_stream(dane: PytanieRequest):
    """Endpoint przyjmujący pytanie w formacie JSON i zwracający odpowiedź token po tokenie."""
    if not HF_TOKEN:
        raise HTTPException(
            status_code=500, 
            detail="Brak skonfigurowanej zmiennej środowiskowej HF_TOKEN w panelu Render."
        )
        
    return StreamingResponse(
        hf_rag_generator(prompt=dane.prompt),
        media_type="text/plain; charset=utf-8"
    )
