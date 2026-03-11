from fastapi import APIRouter
from api.v1.endpoints import auth, user, products, carts

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(carts.router, prefix="/cart", tags=["cart"])