import sys
import os

# 🔥 FORCE PYTHON TO LOOK IN THE CORRECT SITE-PACKAGES FOLDER
sys.path.insert(0, '/Users/sonikumari/Desktop/resume-checker/backend/venv/lib/python3.13/site-packages')

from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "AI Resume Checker"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"

    SECRET_KEY: str = "development-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()