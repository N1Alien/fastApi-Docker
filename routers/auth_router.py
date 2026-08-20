# Folder: routers/ | Plik: auth_router.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import text
from schemas.auth_chat import UserAuthSchema, TokenSchema
from services.auth_service import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["1. Authentication Management"])

@router.post("/register", summary="Register a brand new corporate user account")
async def register_user(user_data: UserAuthSchema, db: Session = Depends(get_db)):
    """**Registers a new user account inside the persistent cloud infrastructure.**"""
    try:
        existing_user = db.execute(
            text("SELECT id FROM users WHERE email = :email"), 
            {"email": user_data.email}
        ).fetchone()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists.")

        hashed_pwd = hash_password(user_data.password)
        db.execute(
            text("INSERT INTO users (email, password) VALUES (:email, :password)"),
            {"email": user_data.email, "password": hashed_pwd}
        )
        db.commit()
        return {"status": "success", "message": "User registered successfully."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration database error: {str(e)}")

@router.post("/login", response_model=TokenSchema, summary="Log in to get a secure bearer JWT token")
async def login_user(user_data: UserAuthSchema, db: Session = Depends(get_db)):
    """**Verifies credentials and issues a unique cryptographically signed JSON Web Token (JWT).**"""
    user = db.execute(
        text("SELECT id, password FROM users WHERE email = :email"), 
        {"email": user_data.email}
    ).fetchone()
    
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = create_access_token(user_id=str(user.id))
    return {"access_token": token, "token_type": "bearer"}
