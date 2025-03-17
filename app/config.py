from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    STEAM_URL: str
    METACRITIC_URL: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
