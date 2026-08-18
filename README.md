# ☁️ 100% Cloud-Native Agentic RAG Stack with FastAPI, LangGraph, and PostgreSQL

A cutting-edge, fully autonomous, and production-grade **Agentic RAG (Retrieval-Augmented Generation)** system. This entire ecosystem is built with **FastAPI**, backed by a cloud **PostgreSQL** cluster using the **`pgvector`** extension, and engineered into a singular, self-contained **All-in-One Docker Container** running natively in the chmura. 

By leveraging **LangGraph**, the application transitions from a traditional, linear data pipeline into an intelligent, loop-based cognitive agent capable of multi-step reasoning, tool execution, and dynamic self-correction.

---

## 🌍 The Core Philosophy: 100% Serverless Cloud Infrastructure

This application is **entirely independent of local machine hardware**. It does not require local Python runtimes, local database setups, or local Docker daemons to execute. You can completely shut down your local computer, and the system will remain fully operational, globally accessible via its secure public URL with automated SSL certification.

### Cloud Network Topology:
*   **The Container Ecosystem (Render Web Service):** Encapsulates the FastAPI framework, the Python 3.12 virtual environment, and a fully functional embedded **Ollama AI engine** within a single cloud-hosted Docker layer.
*   **The Vector Database Layer (Render PostgreSQL):** A fully managed, decoupled cloud PostgreSQL instance with the native C-compiled `vector` extension enabled (`pgvector`), processing mathematical similarity operations on persistent cloud storage.
*   **The Generative Cognition Layer (Google AI Studio Cloud):** Strategic reasoning and natural language synthesis are securely delegated via cloud-to-cloud HTTPS handshakes to Google's flagship production model (**`gemini-3.6-flash`**).

---

## 🧠 The Agentic Cognitive Architecture (LangGraph Engine)

Unlike standard RAG architectures that strictly search a database and dump text, this system utilizes a **State-Driven Directed Graph with Cycles (Agent Loop)**. The model acts as an executive decision-maker equipped with autonomous "hands" (Python tools).

```text
               [ Global User Client / Swagger UI Panel ]
                                  │
                                  │ (Secure HTTP POST JSON Payload)
                                  ▼
┌────────────────────────────── RENDER CLOUD CONTAINER ──────────────────────────────┐
│                                                                                    │
│      ┌───────────────────────► [ Node: Agent (LLM) ] ───────────────────────┐      │
│      │                                  │                                   │      │
│      │                                  │ (Conditional Edge Evaluation)     │      │
│      │                                  ▼                                   │      │
│      │                        [ Decision: Tool Calls? ]                     │      │
│      │                         /                     \                      │      │
│      │                   (Yes) /                       \ (No)               │      │
│      │                        ▼                         ▼                   │      │
│      │               [ Node: Tool Executor ]         [ END ] ───────────────┼──────┐
│      │                /                   \                                 │      │
│      │               ▼                     ▼                                │      │
│      │     [ Tool: System Date ]  [ Tool: pgvector RAG ]                    │      │
│      │               │                     │                                │      │
│      │               │ (Returns Value)     │ (Queries 768-dim Embeddings)   │      │
│      │               ▼                     ▼                                │      │
│      └──────── [ State Updated ]    [ CLOUD POSTGRESQL ]                     │      │
│                                                                                    │      │
└────────────────────────────────────────────────────────────────────────────────────┘      │
                                                                                            │ (Immediate Token Stream)
                                                                                            ▼
                                                                                   [ Global User Client ]
```

### The Multi-Step Execution Flow:
1.  **State Initialization:** The user’s request enters the graph and initializes the `AgentState` message sequence.
2.  **Cognitive Evaluation (`agent` Node):** Gemini 3.6 Flash assesses the state. It determines if it lacks information to fulfill the user's explicit logic (e.g., temporal calculations or domain knowledge).
3.  **Conditional Routing (`should_continue` Edge):** 
    *   If Gemini requests automated actions, the graph branches into the **`tools` Node**.
    *   If the reasoning is complete, the graph terminates (`END`) and streams the finalized text.
4.  **Autonomous Tool Execution (`tools` Node):** The system dynamically invokes the selected Python tools:
    *   📅 **`get_current_date`**: Fires a system-level clock call inside the container, injecting the exact real-time cloud calendar data into the agent's memory block.
    *   🗄️ **`search_week6_database`**: Passes text parameters into the local Ollama **`nomic-embed-text`** instance, creates a 768-dimensional matrix, and executes a Cosine Distance Similarity query (`<=>`) against the live cloud database, returning the top 6 most relevant document chunks (`LIMIT 6`).
5.  **Feedback Loop (The Cycle):** The tool results are structuralized into `ToolMessage` nodes, injected back into the central state, and routed straight back to the `agent` node. The LLM re-evaluates the expanded memory and can trigger additional tool cycles if required.

---

## 🚀 Optimized Ingestion Pipeline (`/upload-pdf`)

*   **Memory-Buffered Text Extraction:** Incoming PDF files (such as ancient historical texts, corporate manifests, or technical documents) are processed entirely in-memory via an un-cached `pypdf` stream reader.
*   **Overlapping Chunking Layer:** Documents are dynamically sliced into granular blocks (`chunk_size=400`, `overlap=50`) to eliminate semantic truncation at hard pagination splits.
*   **Zero-Cost Native Embedding Pipelines:** Text slices are indexed inside your own cloud container using Ollama's embedded libraries. This layout bypasses expensive third-party embedding tokens, allowing **limitless document processing completely for free**.
*   **Type-Safe Database Rifting:** Floating-point matrices are bound into safe, clean strings and committed to the remote database via standard SQL **`CAST(:variable AS vector)`** syntax, avoiding library-level compiler bugs.

---

## 📈 Public Endpoints & Data Contracts

The microservice exposes an interactive **Swagger UI Documentation Suite** at `/docs`:

### 📁 `POST /upload-pdf`
*   **Payload Type:** `multipart/form-data` (Binary file streaming)
*   **Action:** Triggers extraction, structural alignment, local-container embedding, and inserts the data into the cloud-hosted `ollama_documents` table.
*   **Contract Response:**
    ```json
    {
      "status": "success",
      "indexed_chunks": 15,
      "file_name": "third_letter_of_john.pdf"
    }
    ```

### 💬 `POST /chat-with-model`
*   **Payload Type:** `application/json`
*   **Payload Format:**
    ```json
    {
      "prompt": "Based on the Week 6 document, calculate exactly how many years have passed since the Third Letter of John was written in 90 AD up until today."
    }
    ```
*   **Action:** Runs the LangGraph loop, activates system date tracking and vector database similarity lookups, calculates the math, and returns a clean streamed response block.

---

## 📦 Local Installation & Environment Execution

To run this production framework in a local sandbox mode:

1. Clone the repository and install the synchronized runtime requirements:
   ```bash
   pip install fastapi uvicorn pydantic psycopg2-binary sqlalchemy pgvector numpy pypdf python-multipart ollama google-genai langchain-google-genai langgraph
   ```
2. Export your direct cloud infrastructure parameters to the terminal context:
   ```bash
   export DATABASE_URL="postgresql://user:password@://render.com"
   export GEMINI_API_KEY="AIzaSyYourPrivateHandshakeKeyFromGoogleAIStudio"
   ```
3. Run the microservice framework locally:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 10000 --reload
   ```
