import uuid

from fastapi import Depends
from fastapi_users.db import (SQLAlchemyBaseUserTableUUID,
                              SQLAlchemyUserDatabase)
from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from src.db.db import Base, engine, get_async_session, metadata


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "app_user"
    fmd = relationship(
        'FileMetaData',
        backref='app_user',
        cascade='all, delete',
    )


class FileMetaData(Base):
    __tablename__ = 'file_data'
    id = Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False)
    path = Column(String(200), nullable=False)
    size = Column(Float(asdecimal=True), nullable=False)
    is_downloadable = Column(String(5), default='True', nullable=False)
    parent_id = Column(ForeignKey('app_user.id', ondelete='cascade'))


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


# async tables init
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
