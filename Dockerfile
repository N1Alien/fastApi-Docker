# 1. Budujemy na oficjalnym obrazie Ollamy (gdzie binaria działają bezbłędnie)
FROM ollama/ollama:latest

# 2. Instalujemy Pythona i niezbędne narzędzia systemowe
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv curl && rm -rf /var/lib/apt/lists/*

# 3. Ustawiamy katalog roboczy dla aplikacji FastAPI
WORKDIR /app

# 4. Kopiujemy listę zależności i kod źródłowy
COPY requirements.txt .
COPY main.py .

# 5. Tworzymy i izolujemy środowisko wirtualne Pythona
RUN python3 -m venv /app/venv
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# 6. Skrypt startowy: Aktywujemy środowisko venv i odpalamy procesy sequentially
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 8\n\
\n\
echo "Downloading embedding model..."\n\
ollama pull nomic-embed-text\n\
\n\
echo "Starting FastAPI app..."\n\
# JAWNE WYWOŁANIE UVICORNA BEZPOŚREDNIO Z KATALOGU BINARNEGO ŚRODOWISKA VENV\n\
/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port 10000\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# Wygląd zewnętrzny portu dla chmury Render
EXPOSE 10000

# Resetujemy twardy ENTRYPOINT Ollamy
ENTRYPOINT []

# Uruchamiamy proces przez bash
CMD ["/bin/bash", "/app/start.sh"]
