import os.path

from sqlalchemy.ext.declarative import declarative_base
from typing import List
import json
from fastapi import UploadFile, Depends
from datetime import datetime
from pathlib import Path
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.db import get_async_session
from pydantic import FilePath



def serialize_data(model: declarative_base, data: List[dict]) -> dict:
    table_name = model.__tablename__
    d = {table_name: []}
    cols = []

    for col in model.__table__.columns:
        cols.append(col.key)

    for obj in data:
        entry = dict(zip(cols, obj))
        logging.info('entry', entry)
        d[table_name].append(entry)
    return d


def get_creation_date(path: str) -> datetime:
    cd = os.path.getmtime(path)
    return datetime.utcfromtimestamp(cd)


def check_out_path(path: str, filename: str) -> str:
    _, file_ext = os.path.splitext(filename)
    if file_ext in path:
        return path
    return os.path.join(path, filename)


def get_or_create_path(path: str) -> None:
    full_path = Path(path)
    dir_path = full_path.parent.absolute()
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        logging.info(f'Directory {dir_path} already exists')


async def get_path_by_file_id(
        file_id: str,
        model: declarative_base,
        session: AsyncSession
) -> str:
    query = select(model.path).where(model.id == str(file_id))
    path = await session.execute(query)
    file_path = path.scalar()
    return file_path


async def get_path_to_file(
        path: FilePath,
        session: AsyncSession,
        model: declarative_base
) -> str:
    if '.' in str(path):
        return path
    path_to_file = await get_path_by_file_id(
        path,
        session=session,
        model=model
    )
    return path_to_file



async def count_connection_time(func: callable, **kwargs) -> tuple:
    start = datetime.now()
    try:
        await func(**kwargs)
    except (ConnectionError, FileNotFoundError) as e:
        logging.error(f'failed to {func.__name__}')
        raise e
    else:
        result = (datetime.now() - start).total_seconds()
        logging.info(f'succesfully counted time - {func.__name__}')
    return func.__name__, result


def uuid_row_to_str(uuid_id: str):
    return uuid_id[7:-4]
