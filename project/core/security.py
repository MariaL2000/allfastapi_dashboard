from datetime import datetime, timedelta, timezone
from typing import List, Callable, Optional, Any, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# Importaciones locales (asegúrate de que los archivos existan)
from db.session import get_db, Base
from models import User
from .config import settings

# Configuración de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# --- FUNCIONES DE HASHING ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- FUNCIONES DE JWT ---

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# --- DEPENDENCIAS DE SEGURIDAD (Aquí se resuelve el 'Any') ---

def get_current_user(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(allowed_roles: List[str]) -> Callable:
    """
    Verifica si el usuario tiene uno de los roles permitidos.
    Retorna una función Callable para que Pylance la reconozca.
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # 1. El superusuario siempre tiene acceso
        if current_user.is_superuser:
            return current_user
            
        # 2. Verificamos los roles asociados al usuario
        # Esto asume que en tu modelo User tienes: roles = relationship("UserRole", back_populates="user")
        user_role_names = [ur.role.name for ur in current_user.roles]
        
        if not any(role in allowed_roles for role in user_role_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso denegado. Se requiere uno de estos roles: {allowed_roles}"
            )
        return current_user
        
    return role_checker