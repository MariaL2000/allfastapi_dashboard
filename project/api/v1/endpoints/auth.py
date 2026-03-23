from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.session import get_db
from services.auth_service import AuthService
from core.security import create_access_token, get_current_user
from schemas import schemas
from models.models import RefreshToken, User

router = APIRouter()

@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Crea un nuevo usuario y le asigna el rol base."""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return AuthService.create_user(db, user_in)

@router.post("/login", response_model=schemas.TokenWithRefresh)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Autenticación estándar OAuth2."""
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = AuthService.create_refresh_session(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cierra la sesión eliminando el refresh token de la BD."""
    AuthService.revoke_token(db, refresh_token)
    return None


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(
    payload: schemas.RefreshRequest, # Usando el schema que ya definiste
    db: Session = Depends(get_db)
):
    """Genera un nuevo access_token usando un refresh_token válido."""
    # 1. Buscar el token en la base de datos
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == payload.refresh_token,
        RefreshToken.revoked == False
    ).first()

    # 2. Validaciones de seguridad
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        # Opcional: Borrar el token expirado de la BD
        db.delete(db_token)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # 3. Obtener el usuario y generar nuevo access token
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive or not found")

    new_access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }