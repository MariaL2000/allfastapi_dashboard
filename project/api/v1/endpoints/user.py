from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from schemas import schemas
from  models import models
from core import get_current_user, require_role

router = APIRouter()

@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Retorna el perfil del usuario actual (token owner)"""
    return current_user

@router.get("/", response_model=List[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db), 
    _ = Depends(require_role(['admin']))
):
    """Listado total de usuarios (Solo Admin)"""
    return db.query(models.User).all()