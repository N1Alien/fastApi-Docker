# Folder: routers/ | Plik: chat_router.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from sqlalchemy import text
from schemas.auth_chat import ChatRequestSchema, SessionResponseSchema
from services.auth_service import get_current_user_id
from services.agent_service import langgraph_agent
from langchain_core.messages import HumanMessage, AIMessage

# USUNIĘTO GLOBALNE TAGI Z ROUTERA
router = APIRouter()

# TAG PRZYPISANY INDYWIDUALNIE DO SESJI
@router.post("/chat/sessions", response_model=SessionResponseSchema, tags=["2. Session & History Control"], summary="Initialize a new isolated chat session room")
async def create_chat_session(current_user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """Creates a separate historical session ID for the logged-in user context."""
    try:
        result = db.execute(text("INSERT INTO chat_sessions (user_id) VALUES (:user_id) RETURNING id;"), {"user_id": int(current_user_id)})
        db.commit()
        new_session_id = result.fetchone()
        return {"status": "success", "session_id": new_session_id, "message": "New chat session initiated successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Session generation database error: {str(e)}")

async def agent_stream_generator(prompt: str, session_id: int, user_id: str):
    try:
        session = SessionLocal()
        past_messages_db = session.execute(text("SELECT role, content FROM chat_messages WHERE session_id = :session_id ORDER BY id ASC;"), {"session_id": session_id}).fetchall()
        history = []
        for msg in past_messages_db:
            if msg.role == "user":
                history.append(HumanMessage(content=msg.content))
            else:
                history.append(AIMessage(content=msg.content))
        session.execute(text("INSERT INTO chat_messages (session_id, role, content) VALUES (:session_id, 'user', :content);"), {"session_id": session_id, "content": prompt})
        session.commit()
        session.close()

        inputs = {"messages": history + [HumanMessage(content=prompt)], "user_id": user_id, "is_safe": True}
        result = langgraph_agent.invoke(inputs, config={"recursion_limit": 20})
        
        if not result.get("is_safe", True):
            yield "[SECURITY ALERT: System blocked the response due to a potential security breach attempt.]"
            return
            
        final_message = result["messages"][-1]
        raw_content = final_message.content
        if isinstance(raw_content, list):
            final_text = " ".join([b.get("text", str(b)) if isinstance(b, dict) else getattr(b, "text", str(b)) for b in raw_content]).strip()
        else:
            final_text = str(raw_content).strip()
            
        if final_text:
            session = SessionLocal()
            session.execute(text("INSERT INTO chat_messages (session_id, role, content) VALUES (:session_id, 'assistant', :content);"), {"session_id": session_id, "content": final_text})
            session.commit()
            session.close()
            for word in final_text.split(" "):
                yield word + " "
        else:
            yield "Response content empty."
    except Exception as e:
        yield f"\n[Secure LangGraph Execution Error: {str(e)}]"

# TAG PRZYPISANY INDYWIDUALNIE DO CZATU AGENTA
@router.post("/chat-with-model", tags=["4. Cognitive Agent Chat"], summary="Stream chat requests through automated LangGraph loop")
async def chat_with_model(request_data: ChatRequestSchema, current_user_id: str = Depends(get_current_user_id)):
    """Executes a high-cognition multi-step Agentic RAG loop using LangGraph and Gemini 3.6 Flash."""
    return StreamingResponse(agent_stream_generator(prompt=request_data.prompt, session_id=request_data.session_id, user_id=current_user_id), media_type="text/plain; charset=utf-8")
