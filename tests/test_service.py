from httpx import AsyncClient
import os
from http import HTTPStatus
from conftest import client, ac
from fastapi import UploadFile
import tempfile


async def test_ping(ac: AsyncClient):
    response = await ac.get('/api/ping')
    assert response.status_code == HTTPStatus.OK
