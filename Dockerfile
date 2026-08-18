# 1. Budujemy na oficjalnym obrazie Ollamy
FROM ollama/ollama:latest

# 2. Instalujemy Pythona i niezbędne narzędzia systemowe
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv curl && rm -rf /var/lib/apt/lists/*

# 3. Ustawiamy katalog roboczy dla aplikacji FastAPI
WORKDIR /app

# 4. Kopiujemy wyłącznie plik main.py (omijamy requirements.txt z cache)
COPY main.py .

# 5. Tworzymy środowisko wirtualne Pythona
RUN python3 -m venv /app/venv

# 6. WYMUSZONA INSTALACJA BEZPOŚREDNIA: Wpisujemy pakiety z palca, ignorując cache
RUN /app/venv/bin/pip install --no-cache-dir fastapi uvicorn pydantic psycopg2-binary sqlalchemy pgvector numpy pypdf python-multipart ollama

# 7. Skrypt startowy uruchamiający procesy po kolei
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 8\n\
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
