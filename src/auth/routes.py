import uuid

from fastapi_users import FastAPIUsers

from src.models.models import User
from .user_manager import get_user_manager
from .auth_backend import auth_backend


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)