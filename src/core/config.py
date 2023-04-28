import os
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    db_url: str = Field(..., env='DATABASE_URL')
    project_name: str = Field(..., env='PROJECT_NAME')
    host: str = Field(..., env='PROJECT_HOST')
    port: str = Field(..., env='PROJECT_PORT')
    secret: str = Field(..., env='SECRET')  # secret key to encode/decode JWT
    storage_path: str = Field(..., env='STORAGE_PATH')
    # db_url = 'postgresql+asyncpg://postgres:postgres@db:5432/async_5'
    # project_name = 'async_5'
    # host = '0.0.0.0'
    # port = '8000'
    # secret = 'SECRET'
    # storage_path = 'storage'


settings = Settings()
