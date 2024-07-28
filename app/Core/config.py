from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME :str
    SECRET_KEY:str
    DATABASE_URL:str
    JWT_ALGORITHM:str
    ACCESS_TOKEN_EXPIRY:int
    class Config:
        env_file = ".env"

setting = Settings()