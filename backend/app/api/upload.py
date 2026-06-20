from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from app.api.deps import get_current_user
import os
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class UploadSignRequest(BaseModel):
    folder: str
    filename: str
    contentType: str


def _generate_presigned_url(folder: str, filename: str, content_type: str, allowed_folders: dict):
    """Shared helper to generate a presigned R2 upload URL."""
    R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID')
    R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
    R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
    R2_PRIVATE_BUCKET = os.environ.get('R2_PRIVATE_BUCKET', 'pyramyd-private')
    R2_PUBLIC_BUCKET = os.environ.get('R2_PUBLIC_BUCKET', 'pyramyd-public')

    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        logger.error("R2 credentials not configured")
        raise HTTPException(status_code=500, detail="Storage service not configured. Please contact support.")

    if folder not in allowed_folders:
        logger.warning(f"Invalid folder requested: {folder}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid folder: {folder}. Allowed: {', '.join(allowed_folders.keys())}"
        )

    folder_config = allowed_folders[folder]
    bucket = folder_config['bucket'].replace('{private}', R2_PRIVATE_BUCKET).replace('{public}', R2_PUBLIC_BUCKET)
    # resolve actual bucket name
    bucket = R2_PRIVATE_BUCKET if folder_config['privacy'] == 'private' else R2_PUBLIC_BUCKET

    file_ext = filename.split('.')[-1] if '.' in filename else ''
    unique_filename = f"{uuid.uuid4()}.{file_ext}" if file_ext else str(uuid.uuid4())
    key = f"{folder}/{unique_filename}"

    import boto3
    from botocore.client import Config

    s3_client = boto3.client(
        's3',
        endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4')
    )

    upload_url = s3_client.generate_presigned_url(
        'put_object',
        Params={'Bucket': bucket, 'Key': key, 'ContentType': content_type},
        ExpiresIn=3600
    )

    public_url = f"https://pub-{R2_ACCOUNT_ID}.r2.dev/{key}" if folder_config['privacy'] == 'public' else key

    return {"uploadUrl": upload_url, "publicUrl": public_url, "key": key}


@router.post("/sign-registration")
async def sign_registration_upload(request: UploadSignRequest):
    """
    PUBLIC endpoint — no authentication required.
    Used during registration BEFORE the user has a JWT token.
    Only allows uploads to the 'user-registration' folder.
    Rate limiting is handled at the nginx/CDN level.
    """
    # Hard-lock: only the registration folder is allowed here
    if request.folder != 'user-registration':
        raise HTTPException(
            status_code=400,
            detail="This public endpoint only accepts uploads to the 'user-registration' folder."
        )
    try:
        R2_PRIVATE_BUCKET = os.environ.get('R2_PRIVATE_BUCKET', 'pyramyd-private')
        allowed = {
            'user-registration': {'privacy': 'private'}
        }
        result = _generate_presigned_url(
            folder=request.folder,
            filename=request.filename,
            content_type=request.contentType,
            allowed_folders=allowed
        )
        logger.info(f"[PUBLIC] Registration upload URL generated: {result['key']}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Public upload sign error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate upload URL: {str(e)}")

@router.post("/sign-public")
async def sign_public_upload(request: UploadSignRequest, current_user: dict = Depends(get_current_user)):
    """
    Authenticated endpoint — generates presigned URL for file upload to R2/CDN.
    Used for product images, profile pictures, messages, etc. after the user is logged in.
    For pre-registration document uploads, use /sign-registration instead.
    """
    try:
        ALLOWED_FOLDERS = {
            'user-registration': {'privacy': 'private'},
            'messages':          {'privacy': 'private'},
            'notifications':     {'privacy': 'private'},
            'admin':             {'privacy': 'private'},
            'temp':              {'privacy': 'private'},
            'social':            {'privacy': 'public'},
            'products':          {'privacy': 'public'},
            'rfq_images':        {'privacy': 'public'},
            'rfq_docs':          {'privacy': 'public'},
        }
        result = _generate_presigned_url(
            folder=request.folder,
            filename=request.filename,
            content_type=request.contentType,
            allowed_folders=ALLOWED_FOLDERS
        )
        logger.info(f"[AUTH] Upload URL generated: {result['key']}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload sign error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate upload URL: {str(e)}")
