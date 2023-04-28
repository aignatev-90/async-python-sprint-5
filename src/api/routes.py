import os.path

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from http import HTTPStatus
from src.services.crud import show_services_info, get_users, upload_single_file, create_file_metadata
from src.db.db import get_async_session
from src.models.models import User, FileMetaData
from src.auth.user_manager import current_active_user, current_user
import fastapi_users
from src.services.utils import check_out_path, get_or_create_path


router = APIRouter()


@router.get('/users')
async def show_users(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    data = await get_users(model=User, session=session)
    return data


@router.get('/user')
async def get_current_user(user=Depends(current_user)):
    return f"Hello, {user.email}"


@router.get(
    '/ping',
    summary='Status of related services',
    description='Displays time of connection to services used in this API',
    status_code=HTTPStatus.OK,
)
async def show_activity_status(session: AsyncSession = Depends(get_async_session)) -> JSONResponse:
    data = await show_services_info(session=session)
    return JSONResponse(data)


@router.post(
    '/files/upload',
    summary='Upload single file',
    description='Uploads single file to storage,'
                ' creates entry with file info in database and retrieves info. '
                'For authorized users only',
    status_code=HTTPStatus.CREATED,
)
async def upload_file(
        file: UploadFile,
        path: str,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
) -> JSONResponse:

    out_path = check_out_path(path, file.filename)
    get_or_create_path(out_path)
    await upload_single_file(file, out_path)
    data = await create_file_metadata(
        user=user,
        session=session,
        filename=os.path.basename(out_path),
        out_path=out_path,
        model=FileMetaData
    )
    return JSONResponse(data)


# @router.get()