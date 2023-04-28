from src.models.models import User, FileMetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
from typing import List
import os
from src.core.config import settings
from datetime import datetime
import logging
from sqlalchemy import select
from .utils import serialize_data, get_creation_date
from fastapi import UploadFile
import aiofiles
from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError


async def get_users(model: declarative_base, session: AsyncSession):
    query = text(f'SELECT * FROM {model.__tablename__}')
    r = await session.execute(query)
    try:
        res = r.all()
        result = serialize_data(model, res)
    except SQLAlchemyError:
        result = {'status': 'something gone wrong'}
    return result


async def show_services_info(session: AsyncSession) -> dict:
    data = []
    db_time = await count_connection_time(connect_to_db, table=User, session=session)
    folder_time = await count_connection_time(connect_to_storage, storage_path=settings.storage_path)
    data.extend([db_time, folder_time])
    return dict(data)


async def count_connection_time(func: callable, **kwargs) -> tuple:
    start = datetime.now()
    try:
        await func(**kwargs)
    except (ConnectionError, FileNotFoundError):
        result = 'failed to connect'
        logging.error(f'failed to {func.__name__}')
    else:
        result = (datetime.now() - start).total_seconds()
        logging.info(f'succesfully counted time - {func.__name__}')
    return func.__name__, result


async def connect_to_db(table: declarative_base, session: AsyncSession) -> None:
    query = text(f'SELECT 1 FROM {table.__tablename__}')
    r = await session.execute(query)


async def connect_to_storage(storage_path: str) -> None:
    os.listdir(storage_path)


async def upload_single_file(file: UploadFile, path: str) -> None:
    async with aiofiles.open(path, 'wb') as out_file:
        while content := await file.read(1024):
            await out_file.write(content)


async def create_file_metadata(
        user: User,
        session: AsyncSession,
        filename: str,
        out_path: str,
        model: declarative_base,

):
    stmt = insert(model).values(
        {
            'name': filename,
            'created_at': get_creation_date(out_path),
            'path': out_path,
            'size': os.path.getsize(out_path),
            'parent_id': user.id,
         }
    )
    await session.execute(stmt)
    await session.commit()
    logging.info(f'New record in db {model.__tablename__} for file {filename}')
