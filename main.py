import os
import numpy as np
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, Text, select, text
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector

# --- KONFIGURACJA BAZY DANYCH (SQLAlchemy + pgvector) ---
# Pobieramy zmienną środowiskową ustawioną w docker-compose.yml
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app_user:app_password@localhost:5434/app_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

DIMENSIONS = 1536  # Wymiar wektorów OpenAI

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(DIMENSIONS))

# --- INICJALIZACJA FASTAPI ---
# Zmień tę linię na początku pliku main.py:
app = FastAPI(title="FastAPI + PostgreSQL pgvector Docker", version="1.0.0", redirect_slashes=True)


@app.on_event("startup")
def startup_event():
    """Uruchamia się automatycznie przy starcie kontenera FastAPI."""
    with engine.connect() as conn:
        # Włączamy wtyczkę wektorową w bazie danych
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    # Tworzymy tabele, jeśli nie istnieją
    Base.metadata.create_all(engine)
    
    # Opcjonalnie: Dodajemy przykładowe dane na start, jeśli baza jest pusta
    session = SessionLocal()
    if session.query(Document).count() == 0:
        def generate_mock_embedding():
            vec = np.random.randn(DIMENSIONS)
            return (vec / np.linalg.norm(vec)).tolist()
        
        doc1 = Document(content="Sztuczna inteligencja i uczenie maszynowe w chmurze.", embedding=generate_mock_embedding())
        doc2 = Document(content="Przepisy na szybki i smaczny obiad wegetariański.", embedding=generate_mock_embedding())
        session.add_all([doc1, doc2])
        session.commit()
    session.close()

# --- MODELE WALIDACJI (Pydantic) ---
class Uzytkownik(BaseModel):
    imie: str = Field(min_length=2, max_length=50)
    email: str

# --- ENDPOINTY ---

@app.post("/uzytkownicy/")
def utworz_uzytkownika(user: Uzytkownik):
    return {"status": "sukces", "dane": user}

@app.get("/uzytkownicy/{user_id}")
def pobierz_uzytkownika(user_id: int = Path(gt=0)):
    return {"user_id": user_id, "imie": "Jan Kowalski", "siec": "docker-ok"}

@app.get("/szukaj/")
def szukaj(q: str = Query(..., min_length=3), limit: int = Query(default=10, ge=1, le=100)):
    return {"szukana_fraza": q, "limit": limit, "status_bazy": "polaczony_w_sieci"}

@app.post("/szukaj-wektorem/")
def szukaj_wektorem():
    """Generuje losowy wektor zapytania i szuka najbliższego sąsiada w bazie za pomocą pgvector."""
    session = SessionLocal()
    try:
        # Generujemy losowy wektor wyszukiwania
        query_vec = np.random.randn(DIMENSIONS)
        query_embedding = (query_vec / np.linalg.norm(query_vec)).tolist()

        # Szukamy rekordów używając podobieństwa cosinusowego (1 - odległość_cosinusowa)
        stmt = (
            select(Document.content, (1 - Document.embedding.cosine_distance(query_embedding)).label("similarity"))
            .order_by(Document.embedding.cosine_distance(query_embedding))
            .limit(2)
        )
        
        results = session.execute(stmt).all()
        
        wyniki = [{"tresc": row.content, "podobienstwo": round(row.similarity, 4)} for row in results]
        return {"status": "sukces", "wyniki": wyniki}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
