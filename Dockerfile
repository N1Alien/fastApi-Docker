# 1. Budujemy na oficjalnym obrazie Ollamy
FROM ollama/ollama:latest

# 2. Instalujemy Pythona i niezbędne narzędzia systemowe
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv curl && rm -rf /var/lib/apt/lists/*

# 3. Ustawiamy katalog roboczy dla aplikacji FastAPI
WORKDIR /app

# 4. Kopiujemy listę zależności i kod źródłowy
COPY requirements.txt .
COPY main.py .

# 5. Instalujemy biblioteki Pythona bezpośrednio w systemie kontenera
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# 6. Skrypt startowy: Uruchamia Ollamę w tle, pobiera modele, a na końcu odpala FastAPI
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 5\n\
echo "Downloading embedding model..."\n\
ollama pull nomic-embed-text\n\
echo "Downloading LLM model..."\n\
ollama pull llama3.2\n\
echo "Starting FastAPI app..."\n\
python3 -m uvicorn main:app --host 0.0.0.0 --port 10000\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Wygląd zewnętrzny portu dla chmury Render (Render domyślnie szuka portu 10000)
EXPOSE 10000

# Uruchamiamy nasz skrypt startowy
CMD ["/app/start.sh"]
