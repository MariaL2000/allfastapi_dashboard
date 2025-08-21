from .auth import auth_router
from .users import users_router
from .admin import admin_router
from .admin_CRUD import admin_products
from .carts import cart_router


__all__ = [
    "auth_router",
    "users_router", 
    "admin_router",
    "admin_products",
    "cart_router"
]