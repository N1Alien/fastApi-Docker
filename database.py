# Folder: główny / Plik: database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

# POPRAWKA KLASY ENTERPRISE DLA BAZ CHMUROWYCH NEON/SUPABASE:
# 1. pool_pre_ping=True - Przed każdym zapytaniem SQL wysyła lekki ping testowy. Jeśli połączenie SSL padło, automatycznie je odnawia.
# 2. pool_recycle=300 - Bezpiecznie zamyka i stawia na nowo wątki z puli co 5 minut, wyprzedzając automatyczne timeouty serwera proxy.
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, 
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Dependency Injection do automatycznego otwierania i zamykania sesji bazy."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
