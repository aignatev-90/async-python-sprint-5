import uuid
from datetime import datetime, timezone
from sqlalchemy import (JSON, DateTime, Column, ForeignKey,
                        Integer, String, MetaData, Float, Table)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship
import asyncio
from src.db.db import Base, engine, get_async_session, metadata
from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


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
        # await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

