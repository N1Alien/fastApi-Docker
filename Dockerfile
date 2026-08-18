# 1. Budujemy na oficjalnym obrazie Ollamy
FROM ollama/ollama:latest

# 2. Instalujemy Pythona i niezbędne narzędzia systemowe
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv curl && rm -rf /var/lib/apt/lists/*

# 3. Ustawiamy katalog roboczy dla aplikacji FastAPI
WORKDIR /app

# 4. Kopiujemy listę zależności i kod źródłowy
COPY requirements.txt .
COPY main.py .

# 5. Tworzymy czyste środowisko wirtualne Pythona i instalujemy zależności
RUN python3 -m venv /app/venv
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# 6. Skrypt startowy: Uruchamia Ollamę, pobiera lekki model i odpala FastAPI z venv
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 5\n\
echo "Downloading embedding model..."\n\
ollama pull nomic-embed-text\n\
echo "Starting FastAPI app..."\n\
/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port 10000\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Wygląd zewnętrzny portu dla chmury Render
EXPOSE 10000

# Resetujemy entrypoint Ollamy, aby kontener pozwolił na odpalenie skryptu bash
ENTRYPOINT []

# Uruchamiamy nasz skrypt startowy przez powłokę systemową
CMD ["/bin/bash", "/app/start.sh"]
