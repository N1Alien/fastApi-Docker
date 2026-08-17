import os
import io
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import google.generativeai as genai
from pypdf import PdfReader

# --- 1. Konfiguracja bazy danych (PostgreSQL + pgvector z Rendera) ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# --- 2. Konfiguracja oficjalnego SDK Google Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(title="RAG z PDF i pgvector w Chmurze", version="2.0.0", redirect_slashes=True)

class PytanieRequest(BaseModel):
    prompt: str

def podziel_tekst(tekst: str, rozmiar: int = 400, overlap: int = 50):
    """Prosta strategia chunkingu z nakładaniem się (overlap)."""
    kawałki = []
    start = 0
    dlugosc = len(tekst)
    while start < dlugosc:
        koniec = start + rozmiar
        kawałki.append(tekst[start:koniec])
        start += rozmiar - overlap
    return [k.strip() for k in kawałki if k.strip()]

# --- 3. Endpoint wczytujący plik PDF, chunking i zapis embeddingów ---
@app.post("/wczytaj-pdf")
async def wczytaj_pdf(file: UploadFile = File(...)):
    """Wczytuje plik PDF, ekstrahuje tekst, dzieli na chunki, wektoryzuje i zapisuje w bazie wektorowej."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Brak klucza GEMINI_API_KEY.")
        
    try:
        # Odczyt zawartości pliku PDF w pamięci RAM
        pdf_bytes = await file.read()
        pdf_stream = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_stream)
        
        pelny_tekst = ""
        for page in reader.pages:
            tekst_strona = page.extract_text()
            if tekst_strona:
                pelny_tekst += tekst_strona + "\n"
                
        if not pelny_tekst.strip():
            raise HTTPException(status_code=400, detail="Nie udało się odczytać tekstu z tego pliku PDF.")
            
        # Podział tekstu na mniejsze kawałki (chunky)
        chunky = podziel_tekst(pelny_tekst)
        
        # Inicjalizacja modelu embeddingów od Google
        # Zapis do bazy danych PostgreSQL z pgvector
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector(3072)
                );
            """))
            
            for chunk in chunky:
                # Generowanie embeddingu przez Google SDK
                embed_result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=chunk
                )
                wektor = embed_result["embedding"]
                wektor_str = str(wektor)
                
                conn.execute(
                    text("INSERT INTO documents (content, embedding) VALUES (:content, :embedding::vector)"),
                    {"content": chunk, "embedding": wektor_str}
                )
                
        return {"status": "success", "zindeksowano_fragmentow": len(chunky), "nazwa_pliku": file.filename}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd przetwarzania PDF: {str(e)}")

# --- 4. Inteligentny generator oparty na wyszukiwaniu w bazie wektorowej ---
async def smart_rag_generator(prompt: str):
    """Wyszukuje pasujący fragment przez wektory w pgvector i generuje odpowiedź z Gemini."""
    try:
        # Krok A: Generowanie wektora dla pytania użytkownika
        query_embed = genai.embed_content(
            model="models/text-embedding-004",
            content=prompt
        )
        query_vector_str = str(query_embed["embedding"])
        
        # Krok B: Wyszukiwanie pasujących fragmentów (similarity search przez operator <=>)
        session = SessionLocal()
        wyniki = session.execute(
            text("SELECT content FROM documents ORDER BY embedding <=> :qvec::vector LIMIT 3;"),
            {"qvec": query_vector_str}
        ).fetchall()
        session.close()
        
        if wyniki:
            kontekst = "\n---\n".join([row[0] for row in wyniki])
        else:
            kontekst = "Brak pasujących dokumentów w bazie."
            
        # Krok C: Przekazanie kontekstu i promptu do modelu Gemini 3.6 Flash
        model = genai.GenerativeModel('gemini-3.6-flash')
        pelny_prompt = (
            f"Jesteś inteligentnym asystentem. Masz dostęp do bazy wiedzy (fragmentów PDF):\n'{kontekst}'.\n\n"
            f"Jeśli pytanie dotyczy tej wiedzy, wykorzystaj ją. W przeciwnym wypadku odpowiedz "
            f"na podstawie własnej wiedzy ogólnej.\n\n"
            f"Pytanie użytkownika: {prompt}"
        )
        
        response = model.generate_content(pelny_prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        yield f"\n[Błąd chmurowego RAG: {str(e)}]"

# --- 5. Główny endpoint czatu (zmieniona nazwa z rag-hf-stream) ---
@app.post("/chat-z-modelem")
async def chat_z_modelem(dane: PytanieRequest):
    """Płynny czat z modelem AI wzbogacony o wyszukiwanie w bazie wektorowej."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Brak klucza GEMINI_API_KEY w panelu Render.")
        
    return StreamingResponse(
        smart_rag_generator(prompt=dane.prompt),
        media_type="text/plain; charset=utf-8"
    )
