from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from db import SessionLocal
import models, schemas, auth
from datetime import datetime, timedelta
import os
import requests
from dotenv import load_dotenv

from fastapi.security import OAuth2PasswordRequestForm

load_dotenv()

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@auth_router.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.hash_password(user_in.password)
    user = models.User(name=user_in.name, email=user_in.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@auth_router.post("/login", response_model=schemas.TokenWithRefresh)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access = auth.create_access_token(subject=user.email)
    refresh_token = auth.create_refresh_token()
    expires_at = datetime.utcnow() + timedelta(days=int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '30')))
    rt = models.RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at)
    db.add(rt)
    db.commit()
    return {"access_token": access, "token_type": "bearer", "refresh_token": refresh_token}


@auth_router.post('/refresh', response_model=schemas.Token)
def refresh_token(req: schemas.RefreshRequest, db: Session = Depends(get_db)):
    rt = db.query(models.RefreshToken).filter(models.RefreshToken.token == req.refresh_token, models.RefreshToken.revoked == False).first()
    if not rt:
        raise HTTPException(status_code=401, detail='Invalid refresh token')
    if rt.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail='Refresh token expired')
    user = db.query(models.User).filter(models.User.id == rt.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    access = auth.create_access_token(subject=user.email)
    return {"access_token": access, "token_type": "bearer"}

@auth_router.post('/revoke', status_code=204)
def revoke_token(req: schemas.RefreshRequest, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    rt = db.query(models.RefreshToken).filter(models.RefreshToken.token == req.refresh_token, models.RefreshToken.user_id == current_user.id).first()
    if not rt:
        raise HTTPException(status_code=404, detail='Refresh token not found')
    rt.revoked = True
    db.add(rt)
    db.commit()
    return

# Google OAuth2 (scaffold)
@auth_router.get('/google/login')
def google_login():
    # Redirect the user to Google's OAuth 2.0 server to initiate the authentication flow.
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    redirect = os.getenv('GOOGLE_REDIRECT_URI')
    scope = 'openid email profile'
    state = 'state-example'  # production: create a CSRF-safe random state and store it server-side
    auth_url = ('https://accounts.google.com/o/oauth2/v2/auth'
                f'?client_id={client_id}&response_type=code&scope={scope}'
                f'&redirect_uri={redirect}&state={state}')
    return {'auth_url': auth_url}

@auth_router.get('/google/callback')
def google_callback(request: Request, db: Session = Depends(get_db)):
    # After user authorizes, Google redirects to this endpoint with ?code=...
    code = request.query_params.get('code')
    if not code:
        raise HTTPException(status_code=400, detail='Missing code')
    token_endpoint = 'https://oauth2.googleapis.com/token'
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect = os.getenv('GOOGLE_REDIRECT_URI')
    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect,
        'grant_type': 'authorization_code'
    }
    token_resp = requests.post(token_endpoint, data=data)
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail='Token exchange failed')
    token_json = token_resp.json()
    id_token = token_json.get('id_token')
    # In production verify id_token signature with google-auth library
    # Here we use id_token to extract email via Google's tokeninfo endpoint (note: not for production verification)
    info = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}').json()
    email = info.get('email')
    if not email:
        raise HTTPException(status_code=400, detail='Could not get email from Google')
    # Create or get user
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(name=info.get('name', email.split('@')[0]), email=email, hashed_password=None)
        db.add(user)
        db.commit()
        db.refresh(user)
    # create access + refresh
    access = auth.create_access_token(subject=user.email)
    refresh_token = auth.create_refresh_token()
    expires_at = datetime.utcnow() + timedelta(days=int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '30')))
    rt = models.RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at)
    db.add(rt)
    db.commit()
    return {"access_token": access, "refresh_token": refresh_token}
