import asyncio
import logging
import logging.config
import os
import sys

import uvicorn
import yaml
from fastapi import FastAPI
from watchgod import run_process

# fix import issues
sys.path.insert(0, os.getcwd())

from src.api.routes import router
from src.auth.auth_backend import auth_backend
from src.auth.routes import fastapi_users
from src.core.config import settings
from src.models.models import init_models
from src.models.schemas import UserCreate, UserRead

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/docs',
    openapi_url='/api/openapi.json',
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix='/auth',
    tags=['auth'],
)

app.include_router(
    router,
    prefix='/api',
    tags=['api']
)


def main():
    asyncio.run(init_models())
    with open('src/core/logging_config.yml') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    uvicorn.run(
        'main:app',
        host=settings.host,
        port=int(settings.port),
    )


if __name__ == "__main__":
    run_process(os.getcwd(), main)
