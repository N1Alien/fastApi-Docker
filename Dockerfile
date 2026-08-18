FROM ollama/ollama:latest

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
COPY main.py .

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Pobieramy TYLKO lekki model nomic-embed-text (~280MB), który zmieści się w darmowym RAM-ie
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 5\n\
echo "Downloading embedding model..."\n\
ollama pull nomic-embed-text\n\
echo "Starting FastAPI app..."\n\
python3 -m uvicorn main:app --host 0.0.0.0 --port 10000\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 10000

ENTRYPOINT []

CMD ["/bin/bash", "/app/start.sh"]
