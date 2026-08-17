import os
import json
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI(title="Testowy RAG Gemini w Chmurze", version="1.0.0", redirect_slashes=True)

class PytanieRequest(BaseModel):
    prompt: str

async def temp_gemini_generator(prompt: str):
    try:
        kontekst = "Tymczasowy kontekst testowy: Aplikacja w chmurze Render działa poprawnie."
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"Kontekst: {kontekst}\n\nPytanie: {prompt}"}
                    ]
                }
            ]
        }
        
        API_URL = f"https://googleapis.com{GEMINI_API_KEY}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", API_URL, json=payload) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    yield f"\n[Błąd Gemini API (Status {response.status_code}): {error_text.decode('utf-8')}]"
                    return
                
                async for chunk in response.aiter_text():
                    if chunk:
                        try:
                            cleaned_chunk = chunk.strip().lstrip(',').rstrip(',')
                            if cleaned_chunk.startswith('[') or cleaned_chunk.endswith(']'):
                                continue
                            chunk_json = json.loads(cleaned_chunk)
                            token = chunk_json["candidates"]["content"]["parts"]["text"]
                            if token:
                                yield token
                        except Exception:
                            continue

    except Exception as e:
        yield f"\n[Błąd systemu: {str(e)}]"

@app.post("/rag-hf-stream")
async def rag_hf_stream(dane: PytanieRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Brakuje GEMINI_API_KEY.")
    return StreamingResponse(
        temp_gemini_generator(prompt=dane.prompt),
        media_type="text/plain; charset=utf-8"
    )
