# ☁️ 100% Cloud-Native Production-Ready Hybrid RAG API

A cutting-edge, fully autonomous, and production-grade Retrieval-Augmented Generation (RAG) system. This entire ecosystem is built with **FastAPI**, backed by a cloud **PostgreSQL** cluster using the **`pgvector`** extension, and engineered into a singular **All-in-One Docker Container** running natively in the cloud. It features an ultra-optimized hybrid intelligence pipeline that completely eliminates token generation costs and third-party rate limits for vector processing.

---

## 🌍 The Core Philosophy: 100% Serverless Cloud Infrastructure

This application is **entirely independent of your local machine**. It does not require any local Python runtimes, local databases, or local Docker daemons to execute. You can completely shut down your local computer, and the API will remain live, accessible globally via its secure public URL with automated SSL certification.

### Detailed Cloud Topology:
*   **The Container Ecosystem (Render Web Service):** The entire application logic—including the FastAPI backend, the Python runtime environment, and a fully functional embedded **Ollama** AI engine—is encapsulated inside a single Docker image built and hosted in the cloud.
*   **The Vector Database Layer (Render PostgreSQL):** A fully managed, decoupled cloud PostgreSQL database instance. It has the native C-compiled `vector` extension enabled (`pgvector`), processing mathematical similarity operations on an isolated, persistent cloud storage volume.
*   **The Generative Cognition Layer (Google AI Studio Cloud):** Advanced generative logic and reasoning are securely delegated via encrypted cloud-to-cloud HTTPS channels to Google's flagship production model (**`gemini-3.6-flash`**), utilizing an official developer API handshake that completely bypasses aggressive cloud firewalls or DDoS protection layers.

---

## ⚙️ The Technical RAG Architecture & Ingestion Pipeline

The project implements a highly advanced **Hybrid RAG Model**, splitting the resource-heavy vector indexing and the high-cognition text generation into two distinct, highly efficient specialized streams:

```text
[ Global User Client / Swagger UI ] 
               │
               │ (Secure HTTP POST JSON Payload / Multipart Form Data)
               ▼
┌─────────────────────────────────── RENDER CLOUD CONTAINER ───────────────────────────────────┐
│                                                                                              │
│   [ FastAPI Backend Framework ] <───(Internal Loopback via 127.0.0.1:11434)───> [ Ollama ]   │
│                 │                                                                  │         │
│                 │ (SQL Connection: CAST as Vector)                                 │         │
│                 ▼                                                                  │         │
│   [ CLOUD POSTGRESQL (pgvector) ] <────────────────────────────────────────────────┘         │
│                 │ (Retrieves Exactly 6 Semantic Context Chunks)                              │
│                 ▼                                                                            │
│   [ Encrypted Cloud-to-Cloud Google GenAI SDK Session ]                                      │
│                 │                                                                            │
└─────────────────┼────────────────────────────────────────────────────────────────────────────┘
                  │ (Fires Strict Contextual Augmentation Prompt)
                  ▼
    [ GOOGLE AI CLOUD SERVERS ] ───(Streams 200 OK Token Bundles)───> [ Global User Client ]
```

### 1. Document Ingestion & Unlimited Local-Cloud Chunking (`/upload-pdf`)
*   **Multipart Stream Processing:** PDF files (such as enterprise security guides or massive ethical hacking manuals) are accepted and decoded entirely in-memory using an optimized `pypdf` buffer layer.
*   **Recursive Semantic Chunking:** Text is broken down into structured, overlapping segments (`chunk_size=400`, `overlap=50`) to ensure critical phrases or structural vocabulary are never split at a physical slice boundary.
*   **Zero-Cost Native Embeddings:** Each chunk is passed through the embedded cloud-container Ollama pipeline using the **`nomic-embed-text`** model. This localizes the heavy matrix computations inside your own container, granting you **unlimited, completely free vector generation** with zero API costs.
*   **Mathematical Vector Insertion:** Generated vectors are mapped into a custom **768-dimensional space**. The Python layer translates these numerical matrices into structured strings and commits them to a dedicated, high-performance cloud table (`ollama_documents`) using a secure SQL **`CAST(:variable AS vector)`** protocol to prevent driver level syntax conflicts.

### 2. Contextual Query Augmentation & Streaming (`/chat-with-model`)
*   **Query Vectorization:** The user’s raw text question is instantly converted into a 768-dimensional vector by the container’s local Ollama instance.
*   **Cosine Distance Evaluation:** The API queries the remote PostgreSQL database using the highly optimized **Cosine Distance Vector Operator (`<=>`)**.
*   **Broad Context Extraction (`LIMIT 6`):** The database performs deep matrix multiplication across the multidimensional indexes and extracts exactly the **6 most relevant text fragments** (`LIMIT 6`), guaranteeing that dense documentation across multiple hidden pages is successfully recovered.
*   **Cognitive Text Generation:** The FastAPI layer merges the retrieved knowledge into a strict structural template and hands it over to **Gemini 3.6 Flash** via the modern `google-genai` SDK. Gemini reads the exact facts, processes the logic, and streams a secure, accurate response back to the client.

---

## 🚀 Public API Endpoints

Once deployed, the cloud server exposes an interactive, automated **Swagger UI Documentation Panel** at `/docs`, offering full control over the two production-ready endpoints:

### 📁 `POST /upload-pdf`
*   **Input Type:** `multipart/form-data` (Accepts binary `.pdf` files).
*   **Behavior:** Extracts, slices, generates 768-dim embeddings, and registers the data inside the remote database.
*   **Response:**
    ```json
    {
      "status": "success",
      "indexed_chunks": 42,
      "file_name": "ethical_hacking_bootcamp.pdf"
    }
    ```

### 💬 `POST /chat-with-model`
*   **Input Type:** `application/json`
*   **Payload Format:**
    ```json
    {
      "prompt": "What is a black hat hacker according to the uploaded documentation?"
    }
    ```
*   **Behavior:** Vectorizes the prompt, pulls the 6 closest matching documents via `<=>` sorting, passes them to Gemini 3.6 Flash, and returns a raw streamed text response token by token with an immediate HTTP Status **200 OK**.

---

## 📦 Local Reproduction & Requirements

While designed to live eternally in the cloud, you can run this stack for development purposes.

### 1. Dependencies (`requirements.txt`)
```text
fastapi
uvicorn
pydantic
psycopg2-binary
sqlalchemy
pgvector
numpy
pypdf
python-multipart
ollama
google-genai
```

### 2. Environment Setup
To let the app communicate with the remote database and Google's neural layers, export the required cloud credentials:
```bash
export DATABASE_URL="postgresql://user:password@cloud-host:5432/dbname"
export GEMINI_API_KEY="AIzaSyYourSecretKeyFromGoogleAIStudio"
```

### 3. Execution
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 10000 --reload
```
