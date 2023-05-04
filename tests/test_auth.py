import json
from http import HTTPStatus
from http.cookies import SimpleCookie

import pytest
from conftest import client


#
def test_register():
    response = client.post(
        '/auth/register',
        json={
            "email": "user@example.com",
            "password": "string",
            "is_active": 'true',
            "is_superuser": 'false',
            "is_verified": 'false'
        })
    assert response.status_code == HTTPStatus.CREATED, 'HTTP status error at user registration test'


def test_auth():
    response = client.post(
        'auth/jwt/login',
        data={
            'username': 'user@example.com',
            'password': 'string'
        })
    assert response.status_code == HTTPStatus.OK
