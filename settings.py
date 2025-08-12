

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_DSN:                   str = 'postgresql+asyncpg://pguser:1029384756@localhost:6055/jwt-auth-db'
    SECRET_KEY:                     str = "12345"
    ACCESS_TOKEN_EXPIRE_MINUTES:    int = 1
    REFRESH_TOKEN_EXPIRE_MINUTES:   int = 5
    
    
settings = Settings()
