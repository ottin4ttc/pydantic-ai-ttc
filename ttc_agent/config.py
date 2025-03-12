from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "TTC Agent"
    DATABASE_URL: str = "sqlite:///./chat.db"
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    DMX_API_KEY: str = os.getenv('DMX_API_KEY', '')

    class Config:
        env_file = ".env"

settings = Settings() 