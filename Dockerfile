# 1. Budujemy na oficjalnym obrazie Ollamy
FROM ollama/ollama:latest

# 2. Instalujemy Pythona oraz niezbędne pakiety systemowe
RUN apt-get update && apt-get install -y python3 python3-pip curl && rm -rf /var/lib/apt/lists/*

# 3. Ustawiamy katalog roboczy
WORKDIR /app

# 4. Kopiujemy pliki projektu
COPY requirements.txt .
COPY main.py .

# 5. Bezpieczna globalna instalacja paczek z flagą --break-system-packages
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# 6. Stabilny skrypt startowy z odpowiednim czasem na start serwera Ollama
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 10\n\
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

# Uruchamiamy proces przez bash
CMD ["/bin/bash", "/app/start.sh"]
