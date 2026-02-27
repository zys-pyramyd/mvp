
from fastapi import APIRouter, HTTPException, Depends, status, Request
from app.models.user import User, CreateAdminRequest, UserRole
from app.core.security import hash_password
from app.api.deps import get_db, get_current_user, get_current_admin
from app.core.config import settings
from datetime import datetime, timedelta
import os
import boto3
from botocore.client import Config

router = APIRouter()

# ... existing endpoints ...

# --- KYC Document Management ---
@router.get("/kyc/document/{user_id}/{doc_type}")
async def get_kyc_document(
    user_id: str,
    doc_type: str,
    request: Request,
    current_user: dict = Depends(get_current_admin)
):
    """
    Generate temporary signed URL for admin to view KYC document
    ✅ Audit logged
    ✅ Expires in 1 hour
    ✅ Admin only
    """
    db = get_db()
    
    # 1. Get user
    user = db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Get document metadata
    doc_meta = user.get('documents_submitted', {}).get(doc_type)
    if not doc_meta:
        raise HTTPException(status_code=404, detail=f"Document '{doc_type}' not found for user")
    
    # 3. Get R2 credentials
    R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID')
    R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
    R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
    R2_PRIVATE_BUCKET = os.environ.get('R2_PRIVATE_BUCKET', 'pyramyd-private')
    
    if not all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY]):
        raise HTTPException(status_code=500, detail="Storage not configured")
    
    # 4. Generate signed URL (temporary, 1 hour)
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4')
        )
        
        # Get the key from metadata
        doc_key = doc_meta.get('key') if isinstance(doc_meta, dict) else doc_meta
        
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': R2_PRIVATE_BUCKET,
                'Key': doc_key
            },
            ExpiresIn=3600  # 1 hour
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate signed URL: {str(e)}")
    
    # 5. Audit log
    db.document_access_logs.insert_one({
        "user_id": user_id,
        "document_type": doc_type,
        "accessed_by": current_user['id'],
        "accessed_by_username": current_user.get('username'),
        "accessed_at": datetime.utcnow(),
        "ip_address": request.client.host if request.client else None,
        "action": "view"
    })
    
    # 6. Return signed URL
    return {
        "url": signed_url,
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "document_type": doc_type,
        "file_type": doc_meta.get('file_type') if isinstance(doc_meta, dict) else None,
        "uploaded_at": doc_meta.get('uploaded_at') if isinstance(doc_meta, dict) else None,
        "status": doc_meta.get('status') if isinstance(doc_meta, dict) else 'pending_review'
    }

@router.put("/kyc/document/{user_id}/{doc_type}/status")
async def update_document_status(
    user_id: str,
    doc_type: str,
    status_update: dict,
    current_user: dict = Depends(get_current_admin)
):
    """
    Update document verification status
    Status: approved, rejected, pending_review
    """
    db = get_db()
    
    new_status = status_update.get('status')
    reason = status_update.get('reason', '')
    
    if new_status not in ['approved', 'rejected', 'pending_review']:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Update document status
    result = db.users.update_one(
        {"id": user_id},
        {"$set": {
            f"documents_submitted.{doc_type}.status": new_status,
            f"documents_submitted.{doc_type}.reviewed_at": datetime.utcnow().isoformat(),
            f"documents_submitted.{doc_type}.reviewed_by": current_user['id'],
            f"documents_submitted.{doc_type}.rejection_reason": reason if new_status == 'rejected' else None
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if all documents are approved
    user = db.users.find_one({"id": user_id})
    docs = user.get('documents_submitted', {})
    
    all_approved = all(
        doc.get('status') == 'approved' 
        for doc in docs.values() 
        if isinstance(doc, dict)
    )
    
    if all_approved and docs:
        db.users.update_one(
            {"id": user_id},
            {"$set": {
                "documents_verified": True,
                "documents_verified_at": datetime.utcnow().isoformat(),
                "documents_verified_by": current_user['id']
            }}
        )
    
    return {
        "message": f"Document status updated to {new_status}",
        "all_documents_approved": all_approved
    }
