# Plik: main.py (Zaktualizowana sekcja startowa z CORS)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # DODANY IMPORT
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
    title="🏢 Secure Cloud-Native Agentic Stack (Production Backend)", 
    version="6.2.0", 
    redirect_slashes=True,
    lifespan=lifespan,
    description=(
        "### Welcome to the Production Enterprise RAG Backend API!\n"
        "This panel serves as the secure management layer for company documents and cognitive agents."
    )
)

# --- POPRAWKA PRODUKCYJNA: WŁĄCZENIE CORSMIDDLEWARE ---
# Zezwala Twojej lokalnej aplikacji React na porcie 5174/5173 na bezpieczną rozmowę z chmurą
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Zezwól na ruch ze wszystkich lokalizacji deweloperskich
    allow_credentials=True,
    allow_methods=["*"],  # Zezwól na wszystkie metody HTTP (GET, POST, OPTIONS)
    allow_headers=["*"],  # Zezwól na przesyłanie nagłówków autoryzacji Bearer JWT
)

# Include Router Linkages
app.include_router(auth_router.router)
app.include_router(pdf_router.router)
app.include_router(chat_router.router)
