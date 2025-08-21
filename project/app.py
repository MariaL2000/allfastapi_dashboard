from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from db import engine, Base
import models  
from routes import (
    auth_router, 
    users_router, 
    admin_router, 
    admin_products, 
    cart_router
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI - SQLite + JWT + Roles + Google OAuth2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(admin_products)
app.include_router(cart_router)