from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from models import models #other way to import...
from schemas import schemas 
from core.security import get_current_user

router = APIRouter()

@router.get("/", response_model=schemas.CartOut)
def view_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    cart = db.query(models.Cart).filter(models.Cart.user_id == current_user.id).first()
    if not cart:
        # En lugar de 404, devolvemos un carrito vacío lógico
        return {"id": 0, "items": [], "total": 0.0}
    
    total = sum(item.product.price * item.quantity for item in cart.items)
    return {"id": cart.id, "items": cart.items, "total": total}

@router.post("/items", response_model=schemas.CartOut)
def add_to_cart(
    item_in: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Obtener o crear carrito
    cart = db.query(models.Cart).filter(models.Cart.user_id == current_user.id).first()
    if not cart:
        cart = models.Cart(user_id=current_user.id)
        db.add(cart)
        db.flush() # Para obtener cart.id sin hacer commit aún
    
    # 2. Lógica de producto y cantidad
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id,
        models.CartItem.product_id == item_in.product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += item_in.quantity
    else:
        cart_item = models.CartItem(cart_id=cart.id, **item_in.model_dump())
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart)
    
    total = sum(i.product.price * i.quantity for i in cart.items)
    return {"id": cart.id, "items": cart.items, "total": total}