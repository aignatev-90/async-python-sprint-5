import os
from pydantic import BaseSettings, Field

pg_def_url = 'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres'


class Settings(BaseSettings):
    db_url: str = Field(default=pg_def_url, env='DATABASE_URL')
    project_name: str = Field(default='default', env='PROJECT_NAME')
    host: str = Field(default='default', env='PROJECT_HOST')
    port: str = Field(default='default', env='PROJECT_PORT')
    secret: str = Field(default='default', env='SECRET')  # secret key to encode/decode JWT
    storage_path: str = Field(default='default', env='STORAGE_PATH')


settings = Settings()
