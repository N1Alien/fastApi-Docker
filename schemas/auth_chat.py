# Folder: schemas/ | Plik: auth_chat.py
from pydantic import BaseModel, EmailStr

class UserAuthSchema(BaseModel):
    email: EmailStr
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class ChatRequestSchema(BaseModel):
    session_id: int
    prompt: str

class SessionResponseSchema(BaseModel):
    status: str
    session_id: int
    message: str
