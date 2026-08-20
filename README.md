# ☁️ Secure Cloud-Native Agentic RAG Stack with FastAPI, LangGraph, and PostgreSQL
###  Production-Grade Corporate Documentation Assistant with Multi-Layer Security

---

##  General Project Overview & Business Logic

This application functions as an **Intelligent Corporate Documentation Assistant**. It is engineered to solve a critical enterprise problem: transforming static, unorganized company knowledge (such as PDFs, guidelines, and manuals) into an active, conversational, and highly secure digital asset [1.11]. 

Equipped with an **autonomous cognitive brain**, the assistant doesn't just read documents blindly. It understands user intent, maintains long-term contextual conversation history across rooms, dynamically verifies the current calendar date, and securely queries the global live internet to enrich company documents with real-time global facts [1.7, 1.11].

---

##  The Architectural Manifesto: 100% Cloud-Native & Serverless

This system is built from the ground up to be **entirely decoupled from local physical hardware**. It requires **ZERO** local dependencies, local database clusters, local Python environments, or local background background processes to execute. 

### 🌍 Cloud Independence Framework:
*   **Zero-Hardware Footprint:** You can completely turn off your local machine, and the entire agentic loop remains globally available, online, and accessible via automated cloud network endpoints with integrated SSL certificates.
*   **Cloud-to-Cloud Pipeline:** Document upload, segment chunking, vector calculation, multi-step orchestration, database commits, and public token streaming are processed entirely through synchronized, serverless chmura handshakes.

---

##  Complete Technology Stack & Component Analysis

The system architecture utilizes cutting-edge frameworks across distinct layers, optimized for cost-efficiency, scalability, and top-tier execution safety [1.11, 1.17]:

### 1. Framework & Core API Layer
*   **FastAPI (v0.111+):** High-performance, asynchronous Python web framework used to build production-grade web APIs [1.11]. It handles multi-tenant stream execution, dynamic HTTP dependency injection, and generates interactive Swagger documentation UI in real-time [1.11].
*   **Uvicorn:** A lightning-fast, production-ready ASGI web server implementation used to run the FastAPI app under concurrent load configurations.
*   **Pydantic (v2+):** Advanced data validation and settings management layer [1.11]. It enforces strict, type-safe data schemas (e.g., verifying `EmailStr` structures) before payloads touch database operations.

### 2. Cognitive Agent & Orkiestracja Layer
*   **LangGraph (v0.0.1+):** A specialized framework built by LangChain to compile state-driven **Directed Graphs with Cycles (Agent Loops)** [1.11]. It acts as the core cyfrowy układ nerwowy, allowing the model to cycle through self-correction routines and execute multi-step tools based on active runtime memory [1.11].
*   **LangChain Core (`langchain-core`):** Standardized abstraction layer providing unified interfaces for chat message data types (`HumanMessage`, `AIMessage`, `ToolMessage`) and decorator-level functional tool bindings [1.11].
*   **ChatGoogleGenerativeAI (`langchain-google-genai`):** Official enterprise bridge connecting our cloud app securely to Google's next-generation production LLM model (**`gemini-3.6-flash`**) via cloud-to-cloud JSON requests [1.7].

### 3. Persistent Database & Search Radar Layer
*   **PostgreSQL with `pgvector`:** Relational database cluster deployed in the cloud, configured with a native C-compiled extension (`pgvector`) to perform high-speed mathematical Cosine Distance Similarity operations (`<=>`) on 768-dimensional floating-point arrays.
*   **SQLAlchemy (v2.0+):** High-grade Object-Relational Mapper (ORM) used to handle transaction sessions, execute parameterized text queries safely against SQL injections, and map tables to persistent cloud disks [1.11].
*   **Ollama Embedded Core:** Deployed natively inside the server container layer, running a local **`nomic-embed-text`** engine [1.11]. It converts raw text chunks into 768-dimensional matrices entirely inside the server RAM, providing **limitless, secure vector generation completely for free (0$ token bills)** [1.11].
*   **Tavily Search API:** An advanced search engine engine explicitly optimized for AI agents and LLMs [1.11]. It bypasses front-end visual junk (ads/HTML layout) and returns structured, clear, and summarized web content snippets in real-time [1.11].

### 4. Security & Cryptography Layer
*   **Bcrypt Native Szyfrowanie:** Direct cryptographic hashing implementation [1.11]. Passwords are safe-salted and hashed at a hardware-byte level before hitting tables, matching banking-grade storage profiles.
*   **PyJWT:** Professional signature token generator [1.11]. It issues securely encoded JSON Web Tokens (JWT) with automated 60-minute expiration lifespans to guard API routes [1.11].
*   **XML Security Tagging:** System wrapper that packs untrusted text extractions inside strict `<context>` tags [1.7], forcing the LLM to treat document data strictly as raw passive inputs rather than executable system commands.

---

##  Production Modular Directory Layout

The system architecture implements clean separation of concerns by partitioning logic into standalone architectural directory layers [1.11]:

```text
/app
├── main.py                 # System launcher, async lifecycle lifespan database migrator
├── database.py             # Central SQLAlchemy connection pooling & Dependency Injector
├── Dockerfile              # Complete Linux build matrix with C compilers & dev dependencies
├── models/
│   └── tables.py           # Persistent SQLAlchemy ORM database schema specifications
├── schemas/
│   └── auth_chat.py        # Strict input/output payload validation templates via Pydantic
├── services/
│   ├── auth_service.py     # Password hashing, token encoding, and secure JWT bearer guards
│   ├── pdf_service.py      # PDF binary stream memory readers and local vector embedding
│   ├── internet_service.py # Tavily Search API client connections for real-time web scouting
│   └── agent_service.py    # Complete LangGraph graph layout, tool maps, and Guardrail logic
└── routers/
    ├── __init__.py         # Python packaging folder initializer
    ├── auth_router.py      # User authentication endpoint routers (Register/Login)
    ├── pdf_router.py       # Knowledge base data ingestion endpoint routers (Upload)
    └── chat_router.py      # Isolated room sessions and streamed agent czat routers
```

---

##  Cognitive Workflow & Multi-Tool Security Engine

The state graph manages an adaptive execution sequence based on continuous evaluation of the central `AgentState` object [1.11]:

```text
                 [ User Request Client / Swagger UI Panel ]
                                    │
                                    │ (Authorized Bearer JWT Token + JSON Request)
                                    ▼
┌──────────────────────────────── RENDER CLOUD CONTAINER ────────────────────────────────┐
│                                                                                        │
│        ┌────────────────────────► [ Node: Agent (LLM) ] ────────────────────────┐      │
│        │                                   │                                    │      │
│        │                                   │ (Conditional Edge Analysis)        │      │
│        │                                   ▼                                    │      │
│        │                         [ Decision: Tool Calls? ]                      │      │
│        │                          /          │          \                       │      │
│        │                    (Yes) /          │ (Yes)     \ (No)                 │      │
│        │                         ▼           ▼            ▼                     │      │
│        │              [ Tool: Date ] [ Tool: Web ] [ Node: Guardrail ]          │      │
│        │                     │               │            │                     │      │
│        │                     │               │            │ (Verifies           │      │
│        │                     │               │            │  Output Patterns)   │      │
│        │                     ▼               ▼            ▼                     │      │
│        │               [ System Clock ]  [ Tavily API ] [ Routing Edge ]        │      │
│        │                     │               │           /          \           │      │
│        │                     │               │     (Safe)       (Malicious)     │      │
│        │                     ▼               ▼         /              \         │      │
│        └─────────────── [ State Object Updated ]    [ END ]    [ Block Message ] │
│                                                        │               │        │
└────────────────────────────────────────────────────────┼───────────────┼────────┘
                                                         │               │
                                                         ▼               ▼
                                              (Immediate Streamed Chunked Token Response)
```

### Advanced Defensive Layers Enabled:
1.  **Indirect Prompt Injection XML Shields:** Ingested context elements from external files are automatically isolated within structured `<context>` tags [1.7]. A system override instruction explicitly freezes the model from executing any malicious algorithms or programmatic overrides embedded inside the data vectors.
2.  **Row-Level Security Tenant Isolation:** PDF documents and chunked embedding fragments are stamped with the user's secure `user_id` inside the database. Semantic lookups enforce matching ownership clauses, rendering cross-tenant data leaks mathematically impossible.
3.  **Active Output Guardrail Verification:** Before a generated sequence is streamed to the network port, it is intercepted by the `guardrail` node. If pattern-matching filters catch unauthorized system exposures or prompt-breaking tokens (e.g., *"ignore previous instructions"*), the graph flips `is_safe` to `False`, immediately terminates execution, and forces a secure alert override message block.

---

##  Relational Schema Integrity & Cascade Chains

The application configures an enterprise-grade persistent data layout inside the cloud cluster. Foreign key constraints enforce strict transactional synchronization across tables:

*   **`users` Table:** Holds encrypted user accounts (`id`, `email`, `password`). Passwords never touch the disk as plain text; they are encrypted utilizing native byte-level `bcrypt` computations.
*   **`chat_sessions` Table:** Manages isolated chat channels (`id`, `user_id`, `created_at`). It is locked via an active `FOREIGN KEY` tracking back to the user record with an **`ON DELETE CASCADE`** execution instruction.
*   **`chat_messages` Table:** Acts as the persistent long-term historical memory layer (`id`, `session_id`, `role`, `content`, `created_at`). Connected directly to the target chat session using an **`ON DELETE CASCADE`** chain link. If an administrator deletes a session or a user profile from the infrastructure panel, all nested historical messages are cleanly and automatically purged, avoiding database bloating.

---

##  Interaction Protocols & Testing Sequence

The entire decoupled backend exposes an interactive **Swagger UI Documentation Panel** at `/docs` [1.11]:

###  Production Testing Flow:
1.  **Registration:** Issue a `POST` request to `/auth/register` with an email and password string. This triggers the initialization of all relational database tables.
2.  **Login Autoryzacja:** Issue a `POST` request to `/auth/login`. The system validates hashes and yields an encrypted JSON Web Token (JWT).
3.  **Unlocking Swagger:** Copy the raw token string (without quotes). Click the **Authorize** lock icon at the top of the Swagger panel, paste the key, and click close.
4.  **Room Initialization:** Fire a `POST` request to `/chat/sessions` to register an active chat room record. Save the returned `session_id` number (e.g., `1`).
5.  **Data Ingestion:** Ingest your target asset by uploading a binary PDF document via `POST /upload-pdf`.
6.  **Agentic Interrogation:** Fire an HTTP query payload to `POST /chat-with-model` injecting the active `session_id`. Watch LangGraph orchestrate database retrieval, real-time web scouting, and date processing in a unified, safe streamed response loop [1.11]!

---

##  Local Installation & Sandbox Execution (Tryb Deweloperski)

Follow these steps to launch and test this multi-layer backend system in a local development environment:

### 1. Clone the Project & Create Environment
Open your terminal in the project root directory and set up an isolated Python 3.12 virtual environment:
```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual runtime context (Linux / MacOS)
source venv/bin/activate

# Activate the virtual runtime context (Windows PowerShell)
# .\venv\Scripts\Activate.ps1
```

### 2. Install Project Dependencies
Install all synchronized, production-ready ecosystem libraries [1.11]:
```bash
pip install --no-cache-dir fastapi uvicorn pydantic psycopg2-binary sqlalchemy pgvector numpy pypdf python-multipart ollama google-genai langchain-google-genai langgraph bcrypt PyJWT email-validator tavily-python
```

### 3. Setup Local Core AI Services (Ollama Engine)
Ensure you have the Ollama engine running locally to handle embedding vectors:
```bash
# 1. Download and run Ollama from https://ollama.com
# 2. Open a separate terminal and start the server bound to local address:
export OLLAMA_HOST="127.0.0.1:11434"
ollama serve

# 3. Pull the targeted 768-dimensional text embedding model:
ollama pull nomic-embed-text
```

### 4. Inject Environment Handshake Keys
Export your secret API credentials and cloud infrastructure paths directly into your command context:
```bash
export DATABASE_URL="postgresql://user:password@://render.com"
export GEMINI_API_KEY="AIzaSyYourPrivateHandshakeKeyFromGoogleAIStudio"
export TAVILY_API_KEY="tvly-YourPrivateTavilySearchAPIKeyContext"
```

### 5. Launch the FastAPI Uvicorn Server
Execute the asynchronous server thread with hot-reloading active for real-time development [1.11]:
```bash
uvicorn main:app --host 0.0.0.0 --port 10000 --reload
```
Open **`http://localhost:10000/docs`** in your browser to access the complete interactive interface panel!

