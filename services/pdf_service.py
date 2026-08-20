# Folder: services/ | Plik: pdf_service.py
import io
import ollama
from pypdf import PdfReader

ollama_client = ollama.Client(host="http://127.0.0.1:11434")

def split_text(text_content: str, chunk_size: int = 400, overlap: int = 50):
    """Tnie tekst z dokumentów PDF na mniejsze fragmenty."""
    chunks = []
    start = 0
    text_length = len(text_content)
    while start < text_length:
        end = start + chunk_size
        chunks.append(text_content[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]

def extract_and_chunk_pdf(file_bytes: bytes) -> list[str]:
    """Wyciąga tekst ze stron PDF i pakuje go w bezpieczne tagi XML."""
    pdf_stream = io.BytesIO(file_bytes)
    reader = PdfReader(pdf_stream)
    
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += f"<context>\n{page_text}\n</context>\n"
            
    if not full_text.strip():
        return []
        
    return split_text(full_text)

def generate_vector_embedding(text_chunk: str) -> list[float]:
    """Generuje darmowy wektor 768 za pomocą wewnętrznej Ollamy."""
    embed_res = ollama_client.embeddings(model='nomic-embed-text', prompt=text_chunk)
    return embed_res['embedding']
