import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import text
from database import SessionLocal
from routers import auth_router, pdf_router, chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Bezpieczne podnoszenie tabel i kluczy obcych CASCADE na starcie kontenera."""
    session = SessionLocal()
    try:
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            
            CREATE TABLE IF NOT EXISTS chat_messages (
                id SERIAL PRIMARY KEY,
                session_id INT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_session FOREIGN KEY(session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
            );
        """))
        session.commit()
        print("[DATABASE] All layered relational schemas initialized successfully.")
    except Exception as e:
        print(f"[DATABASE ERROR] Failed to initialize relational tables: {str(e)}")
        session.rollback()
    finally:
        session.close()
    yield

app = FastAPI(
    title="🏢 Layered Production Secure Agentic Stack", 
    version="6.0.0", 
    redirect_slashes=True,
    lifespan=lifespan,
    description=(
        "### Welcome to the Layered Architecture Production API Backend!\n"
        "This system has been successfully decoupled into specialized directory layers:\n"
        "`routers/`, `services/`, `models/`, and `schemas/` according to standard enterprise guidelines."
    )
)

# Wstrzykiwanie odseparowanych modułów
app.include_router(auth_router.router)
app.include_router(pdf_router.router)
app.include_router(chat_router.router)
