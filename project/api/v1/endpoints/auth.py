from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.session import get_db
from services.auth_service import AuthService
from schemas import schemas

router = APIRouter()

@router.post("/login", response_model=schemas.TokenWithRefresh)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    
    access_token = AuthService.create_access_token(data={"sub": user.email})
    refresh_token = AuthService.create_refresh_session(db, user.id)
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }

@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    access_token = AuthService.google_oauth_process(db, code)
    return {"access_token": access_token, "token_type": "bearer"}