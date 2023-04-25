from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update
from src.models.models import URLS


async def create(session) -> None:
    async with session() as session:
        async with session.begin():
            session.add(URLS(original_url='or_url', shortened_url='sh_url'))
        await session.commit()
        # data = {'original_url': original_url, 'shortened_url': shortened_url}
        # return data
