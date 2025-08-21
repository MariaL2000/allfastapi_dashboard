from fastapi import APIRouter, Depends, HTTPException
from db import SessionLocal
from sqlalchemy.orm import Session
import models, schemas, auth

admin_router = APIRouter(prefix="/admin", tags=["admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@admin_router.post('/roles', response_model=schemas.RoleOut)
def create_role(payload: schemas.RoleCreate, db: Session = Depends(get_db), _ = Depends(auth.require_role('admin'))):
    existing = db.query(models.Role).filter(models.Role.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail='Role already exists')
    role = models.Role(name=payload.name, description=payload.description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

@admin_router.post('/assign-role')
def assign_role(payload: schemas.AssignRoleRequest, db: Session = Depends(get_db), _ = Depends(auth.require_role('admin'))):
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    role = db.query(models.Role).filter(models.Role.id == payload.role_id).first()
    if not user or not role:
        raise HTTPException(status_code=404, detail='User or Role not found')
    # avoid duplicates
    existing = db.query(models.UserRole).filter(models.UserRole.user_id==user.id, models.UserRole.role_id==role.id).first()
    if existing:
        raise HTTPException(status_code=400, detail='User already has role')
    ur = models.UserRole(user_id=user.id, role_id=role.id)
    db.add(ur)
    db.commit()
    return {'detail': 'role assigned'}
