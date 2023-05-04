import uuid

from src.models.models import User, FileMetaData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
from typing import List
import os
from src.core.config import settings
from datetime import datetime
import logging
from sqlalchemy import select, insert
from .utils import serialize_data, get_creation_date, count_connection_time, uuid_row_to_str
from fastapi import UploadFile
import aiofiles
from sqlalchemy.exc import SQLAlchemyError
import json
from fastapi.encoders import jsonable_encoder


async def get_users(model: declarative_base, session: AsyncSession):
    query = text(f'SELECT * FROM {model.__tablename__}')
    r = await session.execute(query)
    try:
        res = r.all()
        result = serialize_data(model, res)
    except SQLAlchemyError:
        result = {'status': 'something gone wrong'}
    return jsonable_encoder(result)


async def show_services_info(session: AsyncSession) -> dict:
    data = []
    db_time = await count_connection_time(connect_to_db, table=User, session=session)
    folder_time = await count_connection_time(connect_to_repository, repo_path=settings.storage_path)
    data.extend([db_time, folder_time])
    return dict(data)


async def connect_to_db(table: declarative_base, session: AsyncSession) -> None:
    query = text(f'SELECT 1 FROM {table.__tablename__}')
    r = await session.execute(query)


async def connect_to_repository(repo_path: str) -> None:
    os.listdir(repo_path)


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
    # user_id = user.id if user else uuid.uuid4()
    exp = {
            'name': filename,
            'created_at': get_creation_date(out_path),
            'path': out_path,
            'size': os.path.getsize(out_path),
            'parent_id': user_id,
         }
    stmt = insert(model).values(exp)
    result = await session.execute(stmt)
    await session.commit()
    logging.info(f'New record in db {model.__tablename__} for file {filename}')
    if 'is_downloadable' not in exp.keys():
        exp['is_downloadable'] = 'True'
    exp['created_at'] = exp['created_at'].strftime("%d.%m.%Y, %H:%M:%S")
    del exp['parent_id']
    items = list(exp.items())
    items.insert(0, ('id', uuid_row_to_str(str(result.inserted_primary_key))))
    return dict(items)


async def retrieve_files_data(user: User, session: AsyncSession, model: declarative_base):
    query = select(
        model.id,
        model.name,
        model.created_at,
        model.path,
        model.size,
        model.is_downloadable
    ).where(model.parent_id == str(user.id))
    result = await session.execute(query)
    data = {'account_id': str(user.id), 'files': []}
    for row in result:
        data['files'].append(row._asdict())
    return jsonable_encoder(data)
