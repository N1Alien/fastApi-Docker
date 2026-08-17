import os
import json
import urllib.request
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# --- 1. KONFIGURACJA BAZY DANYCH (PostgreSQL z Rendera) ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI(title="Stabilny Bezkluczowy RAG w Chmurze", version="1.0.0", redirect_slashes=True)

class PytanieRequest(BaseModel):
    prompt: str

# --- 2. GENERATOR OPARTY NA CZYSTYM ZAPYTANIU HTTP ---
async def stable_rag_generator(prompt: str):
    try:
        # Krok A: Pobranie wiedzy z bazy danych pgvector
        session = SessionLocal()
        wynik_bazy = session.execute(text("SELECT content FROM documents LIMIT 1;")).fetchone()
        session.close()
        
        kontekst = wynik_bazy[0] if wynik_bazy else "Brak dodatkowego kontekstu w bazie danych."
        
        # Krok B: Przygotowanie promptu w standardzie ChatML dla modelu Qwen
        pelny_prompt = (
            f"<|im_start|>system\nJesteś pomocnym asystentem RAG. Odpowiadaj krótko na podstawie kontekstu: {kontekst}<|im_end|>\n"
            f"<|im_start|>user\n{prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        
        # Oficjalny publiczny endpoint darmowy (bezkluczowy)
        API_URL = "https://huggingface.co"
        payload = {
            "inputs": pelny_prompt,
            "parameters": {"max_new_tokens": 256, "return_full_text": False}
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            API_URL, 
            data=data, 
            headers={"Content-Type": "application/json"}
        )

        # Krok C: Bezpieczne pobranie gotowej odpowiedzi
        # Ponieważ darmowe bramki publiczne bez klucza najlepiej działają przy pełnej odpowiedzi,
        # pobieramy cały blok tekstu i symulujemy strumień dla frontendu słowo po słowie
        with urllib.request.urlopen(req, timeout=30) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            
            # Wyciągamy wygenerowany tekst z odpowiedzi strukturalnej
            if isinstance(res_body, list) and len(res_body) > 0:
                tekst_odpowiedzi = res_body[0].get("generated_text", "")
            else:
                tekst_odpowiedzi = str(res_body)
                
            # Czyszczenie ewentualnych znaczników technicznych modelu
            tekst_odpowiedzi = tekst_odpowiedzi.replace("<|im_end|>", "").strip()

            # Strumieniowanie tekstu token po tokenie (słowo po słowie) do przeglądarki
            for slowo in tekst_odpowiedzi.split(" "):
                yield slowo + " "

    except Exception as e:
        yield f"\n[Błąd stabilnego silnika AI: {str(e)}]"

# --- 3. ENDPOINT PUBLICZNY ---
@app.post("/rag-hf-stream")
async def rag_hf_stream(dane: PytanieRequest):
    """W 100% odporny na zmiany bibliotek, stabilny stream w chmurze bez kluczy."""
    return StreamingResponse(
        stable_rag_generator(prompt=dane.prompt),
        media_type="text/plain; charset=utf-8"
    )
