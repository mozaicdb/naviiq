from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    MONGO_URI: str = os.getenv("MONGO_URI")
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    EMAIL_VERIFY_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_NAME: str = "naviiq_db"

settings = Settings()