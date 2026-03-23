from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from secrets import token_urlsafe
from typing import Optional
from models.models import User, RefreshToken, UserRole, Role
from core.security import get_password_hash, verify_password, create_access_token
from schemas import schemas

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.email == email).first()
        if not user or not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_user(db: Session, user_in: schemas.UserCreate) -> User:
        # 1. Crear el usuario base
        db_user = User(
            name=user_in.name,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            is_active=True,
            is_superuser=False
        )
        db.add(db_user)
        db.flush()  # Para obtener el ID de db_user antes del commit

        # 2. Buscar o crear el rol 'user'
        role = db.query(Role).filter(Role.name == "user").first()
        if not role:
            role = Role(name="user", description="Standard customer access")
            db.add(role)
            db.flush()

        # 3. Crear el vínculo en la tabla asociativa (UserRole)
        # ESTO ES LO QUE LLENA LA LISTA DE ROLES EN TU MODELO
        new_user_role = UserRole(user_id=db_user.id, role_id=role.id)
        db.add(new_user_role)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def create_refresh_session(db: Session, user_id: int) -> str:
        # Invalida tokens anteriores del mismo usuario para mayor seguridad (opcional)
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        
        token = token_urlsafe(64)
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        
        db_token = RefreshToken(
            user_id=user_id, 
            token=token, 
            expires_at=expires
        )
        db.add(db_token)
        db.commit()
        return token

    @staticmethod
    def revoke_token(db: Session, token: str):
        db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if db_token:
            db.delete(db_token)
            db.commit()

    @staticmethod
    def create_refresh_session(db: Session, user_id: int) -> str:
        # Opcional: Rotación de tokens (revocar los anteriores al crear uno nuevo)
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id, 
            RefreshToken.revoked == False
        ).update({"revoked": True})
        
        token = token_urlsafe(64)
        # Importante: Asegúrate de que expires_at guarde la zona horaria si tu BD lo soporta
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        
        db_token = RefreshToken(
            user_id=user_id, 
            token=token, 
            expires_at=expires,
            revoked=False
        )
        db.add(db_token)
        db.commit()
        return token