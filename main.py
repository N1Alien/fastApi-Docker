import os
import io
import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import ollama
from pypdf import PdfReader

# --- IMPORTY DLA SPECYFIKACJI LANGCHAIN & LANGGRAPH ---
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# --- 1. DATABASE CONFIGURATION ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# --- 2. EMBEDDED OLLAMA CONFIGURATION (FOR EMBEDDINGS ONLY) ---
ollama_client = ollama.Client(host="http://127.0.0.1:11434")

# --- 3. DEFINIOWANIE STANÓW DLA LANGGRAPH ---
class AgentState(TypedDict):
    """Pamięć robocza grafu przechowująca sekwencję wiadomości."""
    messages: Annotated[Sequence[BaseMessage], add_messages]

# --- 4. DEFINIOWANIE NARZĘDZI (TOOLS) DLA AGENTA ---
@tool
def get_current_date() -> str:
    """Returns the current precise date and time. Use this whenever the user asks about 'today', 'now', or time differences."""
    now = datetime.datetime.now()
    return f"Current date and time is: {now.strftime('%A, %B %d, %Y, %H:%M:%S')}"

@tool
def search_week6_database(query: str) -> str:
    """Searches the Week 6 internal database (ollama_documents) for context about hacking guidelines, frameworks or threat groups. Input should be a search query string."""
    try:
        query_embed = ollama_client.embeddings(
            model='nomic-embed-text',
            prompt=query
        )
        query_vector_str = str(query_embed['embedding'])
        
        session = SessionLocal()
        db_results = session.execute(
            text("SELECT content FROM ollama_documents ORDER BY embedding <=> CAST(:qvec AS vector) LIMIT 6;"),
            {"qvec": query_vector_str}
        ).fetchall()
        session.close()
        
        if db_results:
            return "\n---\n".join([row[0] for row in db_results])
        return "No matching documents found in the database."
    except Exception as e:
        return f"Error querying database: {str(e)}"

tools = [get_current_date, search_week6_database]
tool_node = ToolNode(tools)

# --- 5. INICJALIZACJA MODELU GEMINI Z WBUDOWANYMI NARZĘDZIAMI ---
# Używamy oficjalnej warstwy LangChain dla Gemini 3.6 Flash
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash", 
    google_api_key=GEMINI_API_KEY,
    temperature=0.1
)
model_with_tools = model.bind_tools(tools)

# --- 6. LOGIKA PRZEPŁYWU GRAFU (GRAPH NODES & EDGES) ---
def call_model(state: AgentState):
    """Węzeł decyzyjny Agenta - przekazuje wiadomości do Gemini."""
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    """Krawędź warunkowa - decyduje, czy model zażądał narzędzia, czy kończymy."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    return "end"

# --- 7. BUDOWANIE I KOMPILACJA GRAFU LANGGRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)

workflow.add_edge("tools", "agent")
langgraph_agent = workflow.compile()

# --- 8. INICJALIZACJA APLIKACJI FASTAPI ---
app = FastAPI(title="LangGraph Agentic RAG Stack in Cloud", version="4.0.1", redirect_slashes=True)

class ChatRequest(BaseModel):
    prompt: str

def split_text(text_content: str, chunk_size: int = 400, overlap: int = 50):
    chunks = []
    start = 0
    text_length = len(text_content)
    while start < text_length:
        end = start + chunk_size
        chunks.append(text_content[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        pdf_bytes = await file.read()
        pdf_stream = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_stream)
        
        full_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
                
        if not full_text.strip():
            raise HTTPException(status_code=400, detail="Could not read text from this PDF file.")
            
        chunks = split_text(full_text)
        
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS ollama_documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector(768)
                );
            """))
            
            for chunk in chunks:
                embed_res = ollama_client.embeddings(
                    model='nomic-embed-text',
                    prompt=chunk
                )
                vector_values = embed_res['embedding']
                vector_str = str(vector_values)
                
                conn.execute(
                    text("INSERT INTO ollama_documents (content, embedding) VALUES (:content, CAST(:embedding AS vector))"),
                    {"content": chunk, "embedding": vector_str}
                )
                
        return {"status": "success", "indexed_chunks": len(chunks), "file_name": file.filename}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")

# --- 9. ENDPOINT CZATU: NAPRAWIONE PARSOWANIE TEKSTU ---
async def agent_stream_generator(prompt: str):
    try:
        inputs = {"messages": [HumanMessage(content=prompt)]}
        config = {"recursion_limit": 20}
        result = langgraph_agent.invoke(inputs, config=config)
        
        final_message = result["messages"][-1]
        raw_content = final_message.content
        
        # NAPRAWIONE: Jeśli content jest listą bloków, scalamy go bezpiecznie w ciąg tekstowy (str)
        if isinstance(raw_content, list):
            clean_text = ""
            for block in raw_content:
                if isinstance(block, dict) and "text" in block:
                    clean_text += block["text"] + " "
                elif hasattr(block, "text"):
                    clean_text += block.text + " "
                else:
                    clean_text += str(block) + " "
            final_text = clean_text.strip()
        else:
            final_text = str(raw_content).strip()
            
        if final_text:
            for word in final_text.split(" "):
                yield word + " "
        else:
            yield "Agent processing complete, but response content was empty."
            
    except Exception as e:
        yield f"\n[LangGraph Execution Error: {str(e)}]"

@app.post("/chat-with-model")
async def chat_with_model(request_data: ChatRequest):
    """Streams responses from automated LangGraph loop integrating remote db context and cloud system date."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GEMINI_API_KEY in Render environment.")
        
    return StreamingResponse(
        agent_stream_generator(prompt=request_data.prompt),
        media_type="text/plain; charset=utf-8"
    )
