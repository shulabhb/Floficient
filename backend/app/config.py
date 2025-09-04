from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    HERE_API_KEY: str
    DATABASE_URL: str

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), ".env")

settings = Settings()
print(f"[DEBUG] config.py loaded. settings: {settings}")
