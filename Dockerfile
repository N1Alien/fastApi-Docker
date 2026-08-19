# 1. Budujemy na oficjalnym obrazie Ollamy
FROM ollama/ollama:latest

# 2. Instalujemy Pythona i niezbędne narzędzia systemowe
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv curl && rm -rf /var/lib/apt/lists/*

# 3. Ustawiamy katalog roboczy dla aplikacji FastAPI
WORKDIR /app

# 4. Kopiujemy plik main.py
COPY main.py .

# 5. Tworzymy środowisko wirtualne Pythona
RUN python3 -m venv /app/venv

# 6. INSTALACJA: Pełen stos technologiczny
RUN /app/venv/bin/pip install --no-cache-dir fastapi uvicorn pydantic psycopg2-binary sqlalchemy pgvector numpy pypdf python-multipart ollama google-genai langchain-google-genai langgraph

# 7. Skrypt startowy uruchamiający procesy po kolei
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 15\n\
\n\
echo "Downloading embedding model..."\n\
ollama pull nomic-embed-text\n\
\n\
echo "Starting FastAPI app..."\n\
/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port 10000\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Wygląd zewnętrzny portu dla chmury Render
EXPOSE 10000

# Resetujemy twardy ENTRYPOINT Ollamy
ENTRYPOINT []

# Uruchamiamy proces przez bash
CMD ["/bin/bash", "/app/start.sh"]