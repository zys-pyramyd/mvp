from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class UploadSignRequest(BaseModel):
    folder: str
    filename: str
    contentType: str

@router.post("/sign-public")
async def sign_public_upload(request: UploadSignRequest):
    """
    Generate presigned URL for file upload to R2/CDN
    Used for registration documents and other uploads
    """
    try:
        # Get R2 configuration
        R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID')
        R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
        R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
        R2_PRIVATE_BUCKET = os.environ.get('R2_PRIVATE_BUCKET', 'pyramyd-private')
        R2_PUBLIC_BUCKET = os.environ.get('R2_PUBLIC_BUCKET', 'pyramyd-public')
        
        # Validate R2 credentials
        if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
            logger.error("R2 credentials not configured")
            raise HTTPException(
                status_code=500, 
                detail="Storage service not configured. Please contact support."
            )
        
        # Folder to bucket mapping (same as server.py)
        ALLOWED_FOLDERS = {
            'user-registration': {'bucket': R2_PRIVATE_BUCKET, 'privacy': 'private'},
            'messages': {'bucket': R2_PRIVATE_BUCKET, 'privacy': 'private'},
            'notifications': {'bucket': R2_PRIVATE_BUCKET, 'privacy': 'private'},
            'admin': {'bucket': R2_PRIVATE_BUCKET, 'privacy': 'private'},
            'temp': {'bucket': R2_PRIVATE_BUCKET, 'privacy': 'private'}, 
            'social': {'bucket': R2_PUBLIC_BUCKET, 'privacy': 'public'},
            'products': {'bucket': R2_PUBLIC_BUCKET, 'privacy': 'public'},
            'rfq_images': {'bucket': R2_PUBLIC_BUCKET, 'privacy': 'public'},   # Bid proof images
            'rfq_docs': {'bucket': R2_PUBLIC_BUCKET, 'privacy': 'public'},     # Contracts/agreements
        }
        
        # Validate folder
        if request.folder not in ALLOWED_FOLDERS:
            logger.warning(f"Invalid folder requested: {request.folder}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid folder: {request.folder}. Allowed: {', '.join(ALLOWED_FOLDERS.keys())}"
            )
        
        folder_config = ALLOWED_FOLDERS[request.folder]
        bucket = folder_config['bucket']
        
        # Generate unique key
        file_ext = request.filename.split('.')[-1] if '.' in request.filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_ext}" if file_ext else str(uuid.uuid4())
        key = f"{request.folder}/{unique_filename}"
        
        logger.info(f"Generating upload URL for: {key} in bucket: {bucket}")
        
        # Initialize R2 client
        import boto3
        from botocore.client import Config
        
        s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4')
        )
        
        # Generate presigned URL for PUT
        upload_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket,
                'Key': key,
                'ContentType': request.contentType
            },
            ExpiresIn=3600  # 1 hour
        )
        
        # Public URL (CDN URL if configured, otherwise R2 URL)
        if folder_config['privacy'] == 'public':
            # Use R2 public URL or your CDN domain
            public_url = f"https://pub-{R2_ACCOUNT_ID}.r2.dev/{key}"
        else:
            # For private files, just return the key
            public_url = key
        
        logger.info(f"Upload URL generated successfully for: {key}")
        
        return {
            "uploadUrl": upload_url,
            "publicUrl": public_url,
            "key": key
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload sign error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate upload URL: {str(e)}"
        )
