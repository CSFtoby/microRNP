from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str = "1521"  # Puerto por defecto de Oracle
    DB_SERVICE_NAME: str
    SOAP_URL: str

    class Config:
        env_file = ".env"
