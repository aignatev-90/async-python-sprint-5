from fastapi import FastAPI, Depends
import uvicorn
import os
import sys
from sqlalchemy import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
#fix import issues
sys.path.insert(0, os.getcwd())

from src.api.routes import router
from src.core.config import settings
from src.models.models import URLS, History
from src.db.db import get_async_session, engine
from src.services.crud import create
from src.auth.routes import fastapi_users
from src.auth.auth_backend import auth_backend
from src.models.schemas import UserRead, UserCreate


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

@app.on_event('startup')
async def startup():
    await create(session=sessionmaker(engine, expire_on_commit=False, class_=AsyncSession))


if __name__ == "__main__":
    uvicorn.run(
        'main:app',
        host=settings.host,
        port=int(settings.port),
    )
