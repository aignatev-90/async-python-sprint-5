from fastapi import FastAPI, Depends
import uvicorn
import os
import sys
from sqlalchemy import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import logging.config
import yaml
import asyncio
from watchgod import run_process

#fix import issues
sys.path.insert(0, os.getcwd())

from src.api.routes import router
from src.core.config import settings
from src.db.db import get_async_session, engine
from src.auth.routes import fastapi_users
from src.auth.auth_backend import auth_backend
from src.models.schemas import UserRead, UserCreate
from src.models.models import init_models



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

# @app.on_event('startup')
# async def startup():
#     await create(session=sessionmaker(engine, expire_on_commit=False, class_=AsyncSession))


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
