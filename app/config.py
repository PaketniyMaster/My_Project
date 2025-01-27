from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    STEAM_URL: str
    METACRITIC_URL: str
    #DATABASE_URL: str
    #SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()