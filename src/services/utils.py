import logging
import os.path
from datetime import datetime
from pathlib import Path

from pydantic import FilePath
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base


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
