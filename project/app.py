
from fastapi import FastAPI
from db.base import Base  
from db.session import engine
from api.v1.api import api_router

# Al importar Base de db.base, SQLAlchemy ya conoce User, Product, etc.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="XHOP'DIT API")

app.include_router(api_router, prefix="/api/v1")