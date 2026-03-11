import os
import requests
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from core.security import create_access_token, verify_password, get_password_hash
from models import models

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user or not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def google_oauth_process(db: Session, code: str):
        # 1. Exchange code for Google tokens
        token_data = {
            "code": code,
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
            "grant_type": "authorization_code",
        }
        resp = requests.post("https://oauth2.googleapis.com/token", data=token_data)
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Google authentication failed")
        
        # 2. Get user info using id_token
        id_token = resp.json().get("id_token")
        info = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}").json()
        email = info.get("email")
        
        # 3. User Upsert
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            user = models.User(
                name=info.get("name", email.split("@")[0]),
                email=email,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        return create_access_token(data={"sub": user.email})

    @staticmethod
    def create_refresh_session(db: Session, user_id: int):
        from secrets import token_urlsafe
        token = token_urlsafe(48)
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        db_token = models.RefreshToken(user_id=user_id, token=token, expires_at=expires)
        db.add(db_token)
        db.commit()
        return token