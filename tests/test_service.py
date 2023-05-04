import os
import tempfile
from http import HTTPStatus

from conftest import ac, client
from fastapi import UploadFile
from httpx import AsyncClient


async def test_ping(ac: AsyncClient):
    response = await ac.get('/api/ping')
    assert response.status_code == HTTPStatus.OK
