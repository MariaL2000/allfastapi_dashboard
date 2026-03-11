from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db.session import get_db
from models import models 
from core.security import require_role
from schemas import schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.ProductOut])
def list_products(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return db.query(models.Product).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.ProductOut)
def create_product(
    product_in: schemas.ProductCreate,
    db: Session = Depends(get_db),
    _ = Depends(require_role("admin"))
):
    db_product = models.Product(**product_in.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    product_in: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    _ = Depends(require_role("admin"))
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _ = Depends(require_role("admin"))
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return None