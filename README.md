# ☁️ Secure Cloud-Native Agentic RAG Stack with FastAPI, LangGraph, and PostgreSQL

A production-grade, highly autonomous, and secure **Agentic RAG (Retrieval-Augmented Generation)** ecosystem. The entire application is packaged into a singular, self-contained **All-in-One Docker Container** running natively in the cloud via **FastAPI**, backed by a cloud **PostgreSQL** cluster using the **`pgvector`** extension.

By migrating to **LangGraph**, the application architecture transitions from a traditional, linear pipeline into an intelligent, loop-based cognitive agent capable of multi-step reasoning, contextual awareness, autonomous tool discovery, and strict output verification through an embedded **Guardrail Node**.

---

## 🌍 The Core Philosophy: 100% Serverless Cloud Infrastructure

This application is **completely independent of local machine hardware**. It requires zero local Python runtimes, local database configurations, or local Docker daemons to execute. You can shut down your machine, and the system remains fully operational, globally accessible via its secure public URL with automated SSL certification.

### Enterprise Cloud Topology:
*   **The Container Ecosystem (Render Web Service):** Encapsulates the FastAPI framework, the isolated Python runtime environment, and a fully functional, embedded **Ollama AI engine** within a single cloud-hosted container layer.
*   **The Vector Database Layer (Render PostgreSQL):** A fully managed, decoupled cloud PostgreSQL instance with the native C-compiled `vector` extension enabled (`pgvector`), processing multidimensional matrix similarity operations on secure cloud volumes.
*   **The Generative Cognition Layer (Google AI Studio Cloud):** Strategic reasoning and natural language synthesis are securely delegated via encrypted cloud-to-cloud HTTPS channels to Google's flagship production model (**`gemini-3.6-flash`**) through the modern `google-genai` layer.

---

## 🧠 The Secure Agentic Cognitive Architecture (LangGraph Engine)

The core execution layer uses a **State-Driven Directed Graph with Cycles (Agent Loop)**. The AI model acts as a real-time executive decision-maker equipped with autonomous "hands" (Python tools), executing in an intelligent, self-correcting feedback loop.

```text
               [ Global User Client / Swagger UI Panel ]
                                  │
                                  │ (Secure HTTP Request with X-User-Id Header)
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
│      │               [ Node: Tool Executor ]      [ Node: Guardrail ]       │      │
│      │                /                   \                 │               │      │
│      │               ▼                     ▼                │ (Is Content   │      │
│      │     [ Tool: System Date ]  [ Tool: Secure RAG ]      │  Safe?)       │      │
│      │               │                     │                ▼               │      │
│      │               │ (Returns Value)     │ (Queries 768)  [ Routing Edge ]       │
│      │               ▼                     ▼               /        \       │      │
│      └──────── [ State Updated ]    [ CLOUD POSTGRESQL ]  (Safe)    (Malicious)    │
│                                                          /            \     │      │
│                                                         ▼              ▼    │      │
│                                                      [ END ]    [ Block Message ]  │
│                                                         │              │           │
└─────────────────────────────────────────────────────────┼──────────────┼───────────┘
                                                          │              │
                                                          ▼              ▼
                                                (Immediate 200 OK Token Stream Output)
```

### Advanced Multi-Step Graph Execution:
1.  **State Initialization:** The incoming payload initializes the `AgentState`, registering the prompt, `user_id` context, and setting the default safety parameter (`is_safe=True`).
2.  **Cognitive Evaluation (`agent` Node):** Gemini 3.6 Flash assesses the current memory state. To protect against **Indirect Prompt Injection**, a strict system boundary prompt is dynamically prepended, forcing the LLM to treat external PDF database data strictly as inert raw variables wrapped in XML tags.
3.  **Conditional Routing (`should_continue` Edge):** 
    *   If Gemini requests tool utilization (Function Calling), the graph branches into the secure execution layer.
    *   If reasoning is complete, the graph flows into the **`guardrail` Node**.
4.  **Row-Level Isolated Tool Execution (`tools` Node):** The system invokes the chosen Python tools:
    *   📅 **`get_current_date`**: Triggers a container-level clock call, injecting real-time cloud calendar data into the agent's memory block.
    *   🗄️ **`search_week6_database`**: Embeds the prompt text into a 768-dimensional matrix using the container's native **`nomic-embed-text`** engine and runs a Cosine Distance Similarity (`<=>`) query against PostgreSQL. It enforces **strict partition isolation via the `user_id` string**, completely preventing cross-tenant data leakage.
5.  **Output Alignment & Threat Mitigation (`guardrail` Node):** Before streaming tokens back to the user, a deep pattern-matching filter intercepts the response. If it flags unauthorized data exposure patterns or prompt-breaking scripts (e.g., *"ignore previous instructions"*), the state flag is flipped to `False`, aborting the response and outputting a hard security alert block.

---

## 🚀 Optimized Data Ingestion Pipeline (`/upload-pdf`)

*   **Memory-Buffered Stream Parsing:** Binary files are processed completely in-memory via an un-cached `pypdf` stream reader buffer layer.
*   **Semantic Chunking & XML Tagging:** Text slices are tokenized into overlapping blocks (`chunk_size=400`, `overlap=50`) and safely wrapped inside structural `<context>` blocks.
*   **Zero-Cost Native Vector Production:** Matrix calculations happen completely inside your cloud container via local Ollama libraries. This localized deployment model bypasses expensive third-party vector generation tokens, granting you **limitless knowledge indexing entirely for free**.

---

## 📊 Public Endpoints & Security Contracts

The application exposes a fully interactive **Swagger UI Panel** at `/docs`:

### 📁 `POST /upload-pdf`
*   **Headers:** `x-user-id` (Defines the isolated database partition owner, defaults to `anonymous_user`).
*   **Payload Type:** `multipart/form-data` (Binary PDF streaming).
*   **Action:** Slices, processes local 768-dim embeddings, and registers the data securely bound to that specific user ID.

### 💬 `POST /chat-with-model`
*   **Headers:** `x-user-id` (Restricts the semantic lookup to matching entries only).
*   **Payload Type:** `application/json`
*   **Contract Payload Example:**
    ```json
    {
      "prompt": "Based on the uploaded document, check how many years have passed since the text was written up until today."
    }
    ```
*   **Action:** Invokes the LangGraph agent, calculates real-time time intervals, validates safety guardrails, and streams a 200 OK safe output block.

---

## 📦 Requirements & Sandboxed Environment Development

### 1. Synchronized Runtime Dependencies (`requirements.txt`)
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
langchain-google-genai
langgraph
```

### 2. Sandbox Execution
```bash
export DATABASE_URL="postgresql://user:password@://render.com"
export GEMINI_API_KEY="AIzaSyYourPrivateHandshakeKeyFromGoogleAIStudio"
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 10000 --reload
```
