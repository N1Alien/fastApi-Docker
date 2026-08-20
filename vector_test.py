import numpy as np
from sqlalchemy import create_engine, Column, Integer, Text, select, text
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector

# 1. Konfiguracja połączenia z bazą danych (port 5434 z Dockera)
DATABASE_URL = "postgresql://myuser:mypassword@localhost:5434/mydb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# 2. Definicja modelu tabeli z kolumną wektorową (1536 wymiarów dla OpenAI)
DIMENSIONS = 1536

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(DIMENSIONS))

# 3. Inicjalizacja bazy danych (Włączenie rozszerzenia i utworzenie tabeli)
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.commit()

Base.metadata.create_all(engine)

# Funkcja pomocnicza do generowania losowych, znormalizowanych wektorów
def generate_mock_embedding():
    vec = np.random.randn(DIMENSIONS)
    return (vec / np.linalg.norm(vec)).tolist()

# 4. Zapisywanie i przeszukiwanie danych w sesji
session = SessionLocal()
try:
    # Czyszczenie tabeli na potrzeby testu
    session.query(Document).delete()
    
    # Tworzenie przykładowych dokumentów
    doc1_embedding = generate_mock_embedding()
    doc2_embedding = generate_mock_embedding()
    
    doc1 = Document(content="Sztuczna inteligencja i uczenie maszynowe.", embedding=doc1_embedding)
    doc2 = Document(content="Przepisy na szybki i smaczny obiad.", embedding=doc2_embedding)
    
    session.add_all([doc1, doc2])
    session.commit()
    print("✓ Pomyślnie zapisano dokumenty i ich wektory w bazie.")

    # 5. Wyszukiwanie najbliższego sąsiada (Podobieństwo Cosinusowe)
    query_embedding = (np.array(doc1_embedding) + np.random.randn(DIMENSIONS) * 0.1)
    query_embedding = (query_embedding / np.linalg.norm(query_embedding)).tolist()

    stmt = (
        select(Document.content, (1 - Document.embedding.cosine_distance(query_embedding)).label("similarity"))
        .order_by(Document.embedding.cosine_distance(query_embedding))
        .limit(2)
    )
    
    results = session.execute(stmt).all()
    
    print("\n--- Wyniki wyszukiwania semantycznego ---")
    for content, similarity in results:
        print(f"Podobieństwo: {similarity:.4f} | Treść: {content}")

finally:
    session.close()

