# 1. Budujemy na oficjalnym obrazie Ollamy
FROM ollama/ollama:latest

# 2. Instalujemy Pythona oraz niezbędne pakiety systemowe
RUN apt-get update && apt-get install -y python3 python3-pip curl && rm -rf /var/lib/apt/lists/*

# 3. Ustawiamy katalog roboczy
WORKDIR /app

# 4. Kopiujemy pliki projektu
COPY requirements.txt .
COPY main.py .

# 5. Instalujemy zależności w przestrzeni użytkownika
RUN pip3 install --no-cache-dir --user -r requirements.txt

# 6. Skrypt startowy ze jawnym eksportem ścieżek Pythona i opóźnieniem
RUN echo '#!/bin/bash\n\
# Wymuszamy, aby Python widział paczki zainstalowane przez --user\n\
export PYTHONPATH="${PYTHONPATH}:/root/.local/lib/python3.12/site-packages:/root/.local/lib/python3.10/site-packages"\n\
export PATH="${PATH}:/root/.local/bin"\n\
\n\
ollama serve &\n\
sleep 7\n\
\n\
echo "Downloading embedding model..."\n\
ollama pull nomic-embed-text\n\
\n\
echo "Starting FastAPI app..."\n\
python3 -m uvicorn main:app --host 0.0.0.0 --port 10000\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Port dla chmury Render
EXPOSE 10000

# Resetujemy twardy entrypoint obrazu bazowego
ENTRYPOINT []

# Uruchamiamy proces
CMD ["/bin/bash", "/app/start.sh"]
