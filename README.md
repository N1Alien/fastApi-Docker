# 100% Cloud-Based RAG API with FastAPI, PostgreSQL, and Google GenAI

A modern, lightweight, and fully cloud-deployed Retrieval-Augmented Generation (RAG) system built with **FastAPI**, backed by a cloud **PostgreSQL** database using the **pgvector** extension, and powered by **Google's Gemini AI**.

---

## ☁️ 100% Cloud Architecture

This project is completely cloud-native and designed to run without local vector database dependencies:
* **Hosting & Backend:** Deployed on **Render Web Service** (running FastAPI & Uvicorn).
* **Vector Database:** Hosted on **Render PostgreSQL** with the `vector` extension enabled (`pgvector`).
* **AI & Embeddings:** Directly integrated with **Google GenAI SDK** via secure cloud API calls (`gemini-embedding-2` for 1536-dimensional vectors and `gemini-3.6-flash` for response generation).

---

## ⚙️ The RAG Workflow & Recent Updates

1. **PDF Ingestion & Chunking (`/upload-pdf`):**
   * Uploaded PDF files are read entirely in-memory using `pypdf`.
   * Text is split into overlapping semantic chunks.
   * Each chunk is embedded into a **1536-dimensional vector** via Google's `gemini-embedding-2`.
   * Vectors and text contents are stored safely inside the cloud PostgreSQL `documents` table using standard SQL `CAST`.

2. **Enhanced Semantic Search & Generation (`/chat-with-model`):**
   * User queries are transformed into 1536-dimensional embeddings on the fly.
   * Cosine distance similarity search (`<=>`) retrieves up to **6 most relevant context chunks** (`LIMIT 6`) from `pgvector` to ensure broader context coverage (e.g., catching specific definitions or deep-page mentions).
   * Retrieved text snippets are injected into the prompt template and streamed back to the user via **Gemini 3.6 Flash**.

---

## 🚀 API Endpoints

* `POST /upload-pdf`: Uploads a `.pdf` file, extracts text, chunks it, generates cloud embeddings (1536 dim), and saves it to `pgvector`.
* `POST /chat-with-model`: Accepts a JSON payload `{ "prompt": "your question" }`, performs an expanded vector similarity search (`LIMIT 6`), and streams a context-aware AI response.

---

## 📦 Installation & Local Development

1. Clone the repository and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up environment variables (`DATABASE_URL` and `GEMINI_API_KEY`).
3. Run the application locally:
   ```bash
   uvicorn main:app --reload
   ```
