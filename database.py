import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    """Dependency Injection do automatycznego otwierania i zamykania sesji bazy."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
