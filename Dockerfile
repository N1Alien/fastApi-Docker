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

# 4. Kopiujemy plik main.py
COPY main.py .

# 5. Tworzymy środowisko wirtualne Pythona
RUN python3 -m venv /app/venv

# 6. Instalacja środowiska z pełnym zestawem bibliotek
RUN /app/venv/bin/pip install --no-cache-dir fastapi uvicorn pydantic psycopg2-binary sqlalchemy pgvector numpy pypdf python-multipart ollama google-genai langchain-google-genai langgraph bcrypt PyJWT email-validator

# 7. POPRAWKA: Czytamy zmienną $PORT dostarczaną przez Render, a jeśli jej nie ma, domyślnie bierzemy 10000
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 15\n\
\n\
echo "Downloading embedding model..."\n\
ollama pull nomic-embed-text\n\
\n\
# Odczytujemy dynamiczny port Rendera i przekazujemy go do Uvicorna\n\
APP_PORT=${PORT:-10000}\n\
echo "Starting FastAPI app on port $APP_PORT..."\n\
/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port "$APP_PORT"\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Wygląd zewnętrzny portu
EXPOSE 10000

ENTRYPOINT []

CMD ["/bin/bash", "/app/start.sh"]
