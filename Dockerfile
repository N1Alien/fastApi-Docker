# 1. Budujemy na oficjalnym, stabilnym obrazie Pythona
FROM python:3.11-slim

# 2. Instalujemy niezbędne narzędzia systemowe (curl do instalacji Ollamy)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 3. Instalujemy Ollamę bezpośrednio w systemie kontenera jednym oficjalnym poleceniem
RUN curl -fsSL https://ollama.com | sh

# 4. Ustawiamy katalog roboczy dla naszej aplikacji
WORKDIR /app

# 5. Kopiujemy pliki projektu
COPY requirements.txt .
COPY main.py .

# 6. Standardowa instalacja bibliotek (na tym obrazie zadziała bez żadnych flag i błędów)
RUN pip install --no-cache-dir -r requirements.txt

# 7. Skrypt startowy: Odpala serwer Ollamy, czeka, pobiera model i podnosi FastAPI
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 8\n\
echo "Downloading embedding model via local Ollama..."\n\
ollama pull nomic-embed-text\n\
echo "Starting FastAPI app..."\n\
uvicorn main:app --host 0.0.0.0 --port 10000\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Port wymagany przez chmurę Render
EXPOSE 10000

# Uruchamiamy proces
CMD ["/bin/bash", "/app/start.sh"]
