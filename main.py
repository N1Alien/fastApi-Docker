# Plik: main.py (PRODUCTION ENTRYPOINT)
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import text
from database import SessionLocal

# Importujemy routery z warstwy routers/
from routers import auth_router, pdf_router, chat_router

# --- 1. LIFESPAN DATABASE INITIALIZER ---
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

# --- 2. FASTAPI SYSTEM INITIALIZATION (PRZYWRÓCONA INSTRUKCJA) ---
app = FastAPI(
    title="🏢 Secure Cloud-Native Agentic Stack (Production Backend)", 
    version="6.1.0", 
    redirect_slashes=True,
    lifespan=lifespan,
    description=(
        "### Welcome to the Production Enterprise RAG Backend API!\n"
        "This panel serves as the secure management layer for company documents and cognitive agents.\n\n"
        "**🚀 PRO-TIP FOR TESTING:**\n"
        "1. Create an account in the **Authentication** section (`/auth/register`).\n"
        "2. Login (`/auth/login`) to receive your unique **JWT Token**.\n"
        "3. Click the **Authorize (lock icon)** button on top of this page, paste the token, and click Authorize.\n"
        "4. Initialize a chat room in the **Session Management** section (`/chat/sessions`) to get a `session_id`.\n"
        "5. Upload documents and stream chat queries safely inside your personal partition!"
    )
)

# --- 3. INCLUDE ROUTERS ---
app.include_router(auth_router.router)
app.include_router(pdf_router.router)
app.include_router(chat_router.router)
