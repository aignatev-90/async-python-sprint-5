import os.path

from fastapi import APIRouter, Depends, UploadFile, Response
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from http import HTTPStatus
from src.services.crud import (
    show_services_info, get_users,
    upload_single_file,
    create_file_metadata, retrieve_files_data,
    )
from src.db.db import get_async_session
from src.models.models import User, FileMetaData
from src.auth.user_manager import current_active_user, current_user
import fastapi_users
from src.services.utils import check_out_path, get_or_create_path, get_path_to_file
import json


router = APIRouter()


@router.get('/users')
async def show_users(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
) -> JSONResponse:
    response = await get_users(model=User, session=session)
    return JSONResponse(response)


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
    response = await show_services_info(session=session)
    return JSONResponse(response)


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
    response = await create_file_metadata(
        user=user,
        session=session,
        filename=os.path.basename(out_path),
        out_path=out_path,
        model=FileMetaData
    )
    return JSONResponse(response) #TODO add jsonresponse


@router.get(
    '/files',
    summary='Get uploaded files data',
    description='Retrieves data about files uploaded by current user.'
                ' For authorized users only',
    status_code=HTTPStatus.OK,
)
async def get_files_data(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    response = await retrieve_files_data(user=user, session=session, model=FileMetaData)
    return JSONResponse(response)

@router.get(
    '/files/download',
    summary='Download file',
    description='Download single file with id or path as query param'
                ' For authorized users only',
    status_code=HTTPStatus.OK
)
async def download_file(
        path: str,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    path_to_file = await get_path_to_file(path, session=session, model=FileMetaData)
    _, filename = os.path.split(path_to_file)
    try:
        return FileResponse(path=path_to_file, media_type='application/octet-stream', filename=filename)
    except FileNotFoundError:
        return JSONResponse({'error': 'file not found'})
