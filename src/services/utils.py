import os.path

from sqlalchemy.ext.declarative import declarative_base
from typing import List
import json
from fastapi import UploadFile
from datetime import datetime
from pathlib import Path
import logging
from uuid import UUID



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
