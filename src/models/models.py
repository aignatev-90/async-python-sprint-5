import uuid
from datetime import datetime, timezone
from sqlalchemy import (JSON, TIMESTAMP, Column, ForeignKey,
                        Integer, String, MetaData, Table)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship
import asyncio
from src.db.db import Base, engine, get_async_session
from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class URLS(Base):
    __tablename__ = 'urls'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_url = Column(String(100), nullable=False)
    shortened_url = Column(String(50), nullable=False)
    click_counter = Column(Integer, default=0, nullable=False)
    history = relationship('History', backref='urls', cascade='all, delete')


class History(Base):
    __tablename__ = 'history'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_url = Column(String(100), nullable=False)
    user_data = Column(JSON)
    used_at = Column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
    parent_id = Column(ForeignKey('urls.id', ondelete='cascade'))
    shortened_url = Column(String(50), nullable=False)
    url = relationship(URLS, backref=backref('children', cascade='all, delete'))


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


# async tables init
async def init_models():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_models())
