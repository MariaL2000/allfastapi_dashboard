import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "XHOP'DIT API"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback_secret_muy_debil")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")

settings = Settings()