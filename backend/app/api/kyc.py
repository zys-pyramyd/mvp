
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Body
from app.api.deps import get_db, get_current_user
from app.models.kyc import KYCDocument, AgentKYC, FarmerKYC
from app.models.common import DocumentType, KYCStatus
from typing import List, Optional
import base64
import uuid
from datetime import datetime

router = APIRouter()

# --- Helper to process file upload ---
async def process_file_upload(file: UploadFile) -> dict:
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, PDF allowed.")
    
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")
        
    encoded_file = base64.b64encode(file_content).decode('utf-8')
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "data": encoded_file,
        "size": len(file_content)
    }

# --- User Endpoints ---

@router.post("/upload-document")
async def upload_document(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a KYC document (ID, Passport, CAC, etc.)"""
    # Validate document type
    try:
        doc_type_enum = DocumentType(document_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid document type. Options: {list(DocumentType)}")
        
    # Process file
    file_info = await process_file_upload(file)
    
    # Create document record
    doc_id = str(uuid.uuid4())
    document = {
        "id": doc_id,
        "user_id": current_user['id'],
        "document_type": doc_type_enum,
        "file_name": file_info['filename'],
        "file_data": file_info['data'], # Base64
        "mime_type": file_info['content_type'],
        "file_size": file_info['size'],
        "uploaded_at": datetime.utcnow(),
        "verified": False
    }
    
    db = get_db()
    db.kyc_documents.insert_one(document)
    
    return {
        "message": "Document uploaded successfully",
        "document_id": doc_id,
        "document_type": document_type
    }

@router.post("/submit/agent")
async def submit_agent_kyc(
    kyc_data: AgentKYC,
    current_user: dict = Depends(get_current_user)
):
    """Submit full Agent KYC application"""
    db = get_db()
    
    # Check if documents exist
    req_docs = [kyc_data.headshot_photo_id, kyc_data.national_id_document_id, kyc_data.utility_bill_id]
    for doc_id in req_docs:
        if doc_id and not db.kyc_documents.find_one({"id": doc_id, "user_id": current_user['id']}):
            raise HTTPException(status_code=400, detail=f"Document {doc_id} not found or doesn't belong to you")

    # Save Agent KYC
    kyc_record = kyc_data.dict()
    kyc_record['user_id'] = current_user['id']
    kyc_record['submitted_at'] = datetime.utcnow()
    
    db.agent_kyc.update_one(
        {"user_id": current_user['id']},
        {"$set": kyc_record},
        upsert=True
    )
    
    # Update User Status
    db.users.update_one(
        {"id": current_user['id']},
        {"$set": {"kyc_status": KYCStatus.PENDING, "kyc_submitted_at": datetime.utcnow()}}
    )
    
    return {"message": "Agent KYC submitted successfully. Pending Admin Review."}

@router.post("/submit/farmer")
async def submit_farmer_kyc(
    kyc_data: FarmerKYC,
    current_user: dict = Depends(get_current_user)
):
    """Submit Farmer KYC application"""
    db = get_db()
    
    # Save Farmer KYC
    kyc_record = kyc_data.dict()
    kyc_record['user_id'] = current_user['id']
    kyc_record['submitted_at'] = datetime.utcnow()
    
    db.farmer_kyc.update_one(
        {"user_id": current_user['id']},
        {"$set": kyc_record},
        upsert=True
    )
    
    # Update User Status
    db.users.update_one(
        {"id": current_user['id']},
        {"$set": {"kyc_status": KYCStatus.PENDING, "kyc_submitted_at": datetime.utcnow()}}
    )
    
    return {"message": "Farmer KYC submitted successfully. Pending Admin Review."}


# --- Admin Endpoints ---

@router.get("/admin/pending")
async def get_pending_kyc(current_user: dict = Depends(get_current_user)):
    """Get all users with pending KYC"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    db = get_db()
    pending_users = list(db.users.find({"kyc_status": KYCStatus.PENDING}))
    
    # Clean up results
    results = []
    for user in pending_users:
        user_id = user['id']
        # Fetch the detailed KYC record based on role
        kyc_details = {}
        documents = []
        
        if user.get('role') == 'agent':
            kyc_details = db.agent_kyc.find_one({"user_id": user_id})
        elif user.get('role') == 'farmer':
            kyc_details = db.farmer_kyc.find_one({"user_id": user_id})
            
        if kyc_details:
            kyc_details.pop('_id', None)
            
            # Fetch document metadata (not the full base64 data to save bandwidth)
            doc_ids = [
                kyc_details.get('headshot_photo_id'),
                kyc_details.get('national_id_document_id'),
                kyc_details.get('utility_bill_id'),
                kyc_details.get('certificate_of_incorporation_id'),
                kyc_details.get('tin_certificate_id')
            ]
            doc_ids = [d for d in doc_ids if d] # filter None
            
            docs = list(db.kyc_documents.find({"id": {"$in": doc_ids}}))
            for d in docs:
                documents.append({
                    "id": d['id'],
                    "type": d['document_type'],
                    "name": d['file_name'],
                    "size": d['file_size'],
                    "verified": d['verified']
                })

        results.append({
            "user_id": user_id,
            "username": user['username'],
            "role": user.get('role'),
            "kyc_data": kyc_details,
            "documents": documents,
            "submitted_at": user.get("kyc_submitted_at")
        })
        
    return results

@router.get("/admin/document/{document_id}")
async def get_document_content(document_id: str, current_user: dict = Depends(get_current_user)):
    """View a specific document content (Base64)"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    db = get_db()
    doc = db.kyc_documents.find_one({"id": document_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    return {
        "file_name": doc['file_name'],
        "mime_type": doc['mime_type'],
        "file_data": doc['file_data'] 
    }

@router.post("/admin/approve/{user_id}")
async def approve_kyc(user_id: str, current_user: dict = Depends(get_current_user)):
    """Approve a user's KYC"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    db = get_db()
    
    # Update User
    result = db.users.update_one(
        {"id": user_id},
        {"$set": {
            "kyc_status": KYCStatus.APPROVED,
            "is_verified": True,
            "kyc_approved_at": datetime.utcnow()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {"message": f"User {user_id} KYC approved and verified."}

@router.post("/admin/reject/{user_id}")
async def reject_kyc(user_id: str, reason: str = Body(..., embed=True), current_user: dict = Depends(get_current_user)):
    """Reject a user's KYC"""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
        
    db = get_db()
    
    db.users.update_one(
        {"id": user_id},
        {"$set": {
            "kyc_status": KYCStatus.REJECTED,
            "is_verified": False
        }}
    )
    
    # Notify user (mock)
    # create_notification(user_id, f"Your KYC was rejected: {reason}")
    
    return {"message": f"User {user_id} KYC rejected."}
