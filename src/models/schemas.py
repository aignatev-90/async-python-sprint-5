import uuid

from fastapi_users import schemas
from pydantic import BaseModel, Field, FilePath, constr
from typing import List

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class ActivityStatus(BaseModel):
    connect_to_db: float = Field(ge=0)
    connect_to_repository: float = Field(ge=0)


class FileCreate(BaseModel):
    id: constr(min_length=36, max_length=36)
    name: str
    created_at: str
    path: str = FilePath
    size: float = Field(ge=0)
    is_downloadable: bool


class FileRead(FileCreate):
    pass


class FilesRead(BaseModel):
    account_id: constr(min_length=36, max_length=36)
    files: List[FileRead]


class ErrorMessage(BaseModel):
    error_message: str
