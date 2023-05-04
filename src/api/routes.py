import logging
import os.path
from http import HTTPStatus

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import FilePath
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.user_manager import current_active_user
from src.db.db import get_async_session
from src.models.models import FileMetaData, User
from src.models.schemas import (ActivityStatus, ErrorMessage, FileCreate,
                                FilesRead)
from src.services.services import (create_file_metadata, retrieve_files_data,
                                   show_services_info, upload_single_file)
from src.services.utils import (check_out_path, get_or_create_path,
                                get_path_to_file)

db_error_message = {'message': 'failed to retrieve data from database'}

router = APIRouter()


@router.get(
    '/ping',
    summary='Status of related services',
    description='Displays time of connection to services used in this API',
    status_code=HTTPStatus.OK,
    response_model=ActivityStatus,
    responses={404: {'model': ErrorMessage}},
)
async def show_activity_status(session: AsyncSession = Depends(get_async_session)):
    try:
        response = await show_services_info(session=session)
        return response
    except (SQLAlchemyError, FileNotFoundError):
        logging.error('failed to connect to sources at ping endpoint')
        return JSONResponse(
            status_code=200,
            content={"error_message": "failed to connect to sources"}
        )


@router.post(
    '/files/upload',
    summary='Upload single file',
    description='Uploads single file to storage,'
                ' creates entry with file info in database and retrieves info. '
                'For authorized users only',
    status_code=HTTPStatus.CREATED,
    response_model=FileCreate,
    responses={500: {'model': ErrorMessage}}
)
async def upload_file(
        file: UploadFile,
        path: str,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):

    out_path = check_out_path(path, file.filename)
    get_or_create_path(out_path)
    try:
        await upload_single_file(file, out_path)
        response = await create_file_metadata(
            user=user,
            session=session,
            filename=os.path.basename(out_path),
            out_path=out_path,
            model=FileMetaData
        )
        return response
    except SQLAlchemyError:
        return JSONResponse(
            status_code=500,
            content=db_error_message
        )


@router.get(
    '/files',
    summary='Get uploaded files data',
    description='Retrieves data about files uploaded by current user.'
                ' For authorized users only',
    status_code=HTTPStatus.OK,
    response_model=FilesRead,
    responses={500: {'model': ErrorMessage}}
)
async def get_files_data(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    try:
        response = await retrieve_files_data(user=user, session=session, model=FileMetaData)
        return response
    except SQLAlchemyError:
        return JSONResponse(
            status_code=500,
            content=db_error_message
        )


@router.get(
    '/files/download',
    summary='Download file',
    description='Download single file with id or path as query param'
                ' For authorized users only',
    status_code=HTTPStatus.OK,
    responses={
        500: {'model': ErrorMessage},
    }
)
async def download_file(
        path: FilePath,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    path_to_file = await get_path_to_file(path, session=session, model=FileMetaData)
    _, filename = os.path.split(path_to_file)
    try:
        return FileResponse(path=path_to_file, media_type='application/octet-stream', filename=filename)
    except SQLAlchemyError:
        return JSONResponse(status_code=500, content=db_error_message)
