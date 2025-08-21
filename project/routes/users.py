from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal
import models, schemas, auth

users_router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Endpoint para usuario logueado ---
@users_router.get("/me", response_model=schemas.UserOut)
def read_users_me(
    current_user: models.User = Depends(auth.get_current_user)
):
    # Mapear los roles correctamente
    roles = [
        {"id": ur.role.id, "name": ur.role.name, "description": ur.role.description}
        for ur in current_user.roles
        if ur.role is not None  # por si hay UserRole huérfano
    ]
    
    return schemas.UserOut.model_validate({
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "roles": roles
    })


# --- Listado de usuarios (solo admins) ---
@users_router.get('/', response_model=list[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db), 
    _ = Depends(auth.require_role(['admin']))
):
    users = db.query(models.User).all()
    
    # Mapear roles de cada usuario
    result = []
    for u in users:
        roles = [
            {"id": ur.role.id, "name": ur.role.name, "description": ur.role.description}
            for ur in u.roles
            if ur.role is not None
        ]
        result.append(schemas.UserOut.model_validate({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "is_active": u.is_active,
            "is_superuser": u.is_superuser,
            "roles": roles
        }))
    
    return result
