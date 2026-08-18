# 1. Oficjalny i stabilny obraz Pythona
FROM python:3.11-slim

# 2. Instalujemy niezbędne narzędzia systemowe (w tym ca/certificates do bezpiecznych pobrań)
RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*

# 3. OMINIĘCIE INSTALATORA: Pobieramy gotowy, skompilowany plik binarny Ollamy dla Linux x86_64
RUN curl -L https://github.com -o /usr/bin/ollama && \
    chmod +x /usr/bin/ollama

# 4. Ustawiamy katalog roboczy dla naszej aplikacji
WORKDIR /app

# 5. Kopiujemy pliki projektu
COPY requirements.txt .
COPY main.py .

# 6. Standardowa i czysta instalacja bibliotek (w tym modułu ollama)
RUN pip install --no-cache-dir -r requirements.txt

# 7. Stabilny skrypt startowy z jawną konfiguracją katalogu modeli
RUN echo '#!/bin/bash\n\
export OLLAMA_MODELS="/app/ollama_models"\n\
mkdir -p /app/ollama_models\n\
\n\
ollama serve &\n\
sleep 8\n\
\n\
echo "Downloading embedding model via local Ollama..."\n\
ollama pull nomic-embed-text\n\
\n\
echo "Starting FastAPI app..."\n\
uvicorn main:app --host 0.0.0.0 --port 10000\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Port wymagany przez chmurę Render
EXPOSE 10000

# Uruchamiamy proces przez powłokę bash
CMD ["/bin/bash", "/app/start.sh"]
