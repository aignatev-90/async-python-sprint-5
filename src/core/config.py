import os
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    db_url: str = Field(..., env='DATABASE_URL')
    project_name: str = Field(..., env='PROJECT_NAME')
    host: str = Field(..., env='PROJECT_HOST')
    port: str = Field(..., env='PROJECT_PORT')
    secret: str = Field(..., env='SECRET') # secret key to encode/decode JWT


settings = Settings()
