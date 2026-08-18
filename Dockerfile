# 1. Budujemy na oficjalnym, stabilnym obrazie Pythona
FROM python:3.11-slim

# 2. Instalujemy niezbędne narzędzia systemowe
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 3. NAPRAWIONE: Oficjalna ścieżka instalacyjna z końcówką /install.sh
RUN curl -fsSL https://ollama.com | sh

# 4. Ustawiamy katalog roboczy dla naszej aplikacji
WORKDIR /app

# 5. Kopiujemy pliki projektu
COPY requirements.txt .
COPY main.py .

# 6. Standardowa instalacja bibliotek bez błędów ścieżek
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

# Uruchamiamy proces przez bash
CMD ["/bin/bash", "/app/start.sh"]
