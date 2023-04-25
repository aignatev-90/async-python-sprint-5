from fastapi import APIRouter, Depends
from src.models.models import URLS, History
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

router = APIRouter()


@router.get('/')
async def show_test_page():
    return {'lol': 'kek'}
        # students.query.all()



