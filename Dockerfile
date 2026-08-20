# 1. Budujemy na oficjalnym obrazie Ollamy
FROM ollama/ollama:latest

# 2. Instalujemy Pythona oraz kompilatory systemowe
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    build-essential \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Ustawiamy katalog roboczy dla aplikacji FastAPI
WORKDIR /app

# 4. POPRAWKA: Kopiujemy całą strukturę projektową (foldery i pliki), a nie tylko main.py
COPY . .

# 5. Tworzymy środowisko wirtualne Pythona
RUN python3 -m venv /app/venv

# 6. Instalacja środowiska z pełnym zestawem bibliotek
RUN /app/venv/bin/pip install --no-cache-dir fastapi uvicorn pydantic psycopg2-binary sqlalchemy pgvector numpy pypdf python-multipart ollama google-genai langchain-google-genai langgraph bcrypt PyJWT email-validator

# 7. Skrypt startowy wymuszający izolację portów
RUN echo '#!/bin/bash\n\
export OLLAMA_HOST="127.0.0.1:11434"\n\
ollama serve &\n\
sleep 15\n\
\n\
echo "Downloading embedding model..."\n\
ollama pull nomic-embed-text\n\
\n\
APP_PORT=${PORT:-10000}\n\
echo "Starting FastAPI app on port $APP_PORT..."\n\
/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port "$APP_PORT"\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 10000
ENTRYPOINT []
CMD ["/bin/bash", "/app/start.sh"]
