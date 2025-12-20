from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import uuid
import boto3
from botocore.client import Config
import os
from database import get_collection
from auth import get_current_user
from .models import Message, MessageCreate

router = APIRouter(prefix="/api", tags=["Messaging"])

# R2 Configuration
R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID')
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
R2_PRIVATE_BUCKET = os.environ.get('R2_PRIVATE_BUCKET', 'pyramyd-private')

s3_client = None
if R2_ACCOUNT_ID and R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY:
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4')
        )
    except Exception:
        pass

# --- ROUTES ---

@router.post("/messages")
async def send_message(msg_data: MessageCreate, current_user: dict = Depends(get_current_user)):
    users_collection = get_collection("users")
    messages_collection = get_collection("messages")
    
    recipient = users_collection.find_one({"username": msg_data.recipient_username})
    if not recipient:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_msg = {
        "id": str(uuid.uuid4()),
        "sender_id": current_user["id"],
        "recipient_id": recipient["id"],
        "content": msg_data.content,
        "attachments": msg_data.attachments,
        "is_read": False,
        "created_at": datetime.utcnow()
    }
    
    messages_collection.insert_one(new_msg)
    new_msg.pop("_id", None)
    return new_msg

@router.get("/conversations")
async def get_conversations(current_user: dict = Depends(get_current_user)):
    messages_collection = get_collection("messages")
    users_collection = get_collection("users")
    
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"sender_id": current_user["id"]},
                    {"recipient_id": current_user["id"]}
                ]
            }
        },
        {"$sort": {"created_at": -1}},
        {
            "$group": {
                "_id": {
                    "$cond": [
                        {"$eq": ["$sender_id", current_user["id"]]},
                        "$recipient_id",
                        "$sender_id"
                    ]
                },
                "last_message": {"$first": "$$ROOT"},
                "unread_count": {
                    "$sum": {
                        "$cond": [
                            {"$and": [
                                {"$eq": ["$recipient_id", current_user["id"]]},
                                {"$eq": ["$is_read", False]}
                            ]},
                            1,
                            0
                        ]
                    }
                }
            }
        }
    ]
    
    conversations = list(messages_collection.aggregate(pipeline))
    results = []
    for conv in conversations:
        other_user_id = conv["_id"]
        user_info = users_collection.find_one({"id": other_user_id}, {"first_name": 1, "last_name": 1, "username": 1, "role": 1, "profile_picture": 1})
        
        if user_info:
            results.append({
                "user": {
                    "id": other_user_id,
                    "username": user_info.get("username"),
                    "first_name": user_info.get("first_name"),
                    "last_name": user_info.get("last_name"),
                    "profile_picture": user_info.get("profile_picture") or "https://via.placeholder.com/40"
                },
                "last_message": {
                    "content": conv["last_message"].get("content"),
                    "created_at": conv["last_message"]["created_at"],
                    "is_own": conv["last_message"]["sender_id"] == current_user["id"]
                },
                "unread_count": conv["unread_count"]
            })
    return {"conversations": results}

@router.get("/messages/{other_username}")
async def get_chat_history(other_username: str, current_user: dict = Depends(get_current_user)):
    users_collection = get_collection("users")
    messages_collection = get_collection("messages")
    
    other_user = users_collection.find_one({"username": other_username})
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    messages = list(messages_collection.find({
        "$or": [
            {"sender_id": current_user["id"], "recipient_id": other_user["id"]},
            {"sender_id": other_user["id"], "recipient_id": current_user["id"]}
        ]
    }).sort("created_at", 1))
    
    for m in messages:
        m.pop("_id", None)
        if m.get("attachments"):
            signed_urls = []
            for key in m["attachments"]:
                try:
                    bucket = R2_PRIVATE_BUCKET
                    if s3_client:
                        url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': bucket, 'Key': key},
                            ExpiresIn=3600
                        )
                        signed_urls.append(url)
                except Exception:
                    signed_urls.append(None)
            m["attachment_urls"] = signed_urls
            
    return {"messages": messages, "other_user_id": other_user["id"]}

@router.post("/messages/read/{sender_username}")
async def mark_messages_read(sender_username: str, current_user: dict = Depends(get_current_user)):
    users_collection = get_collection("users")
    messages_collection = get_collection("messages")
    
    sender = users_collection.find_one({"username": sender_username})
    if not sender:
        raise HTTPException(status_code=404, detail="User not found")
        
    messages_collection.update_many(
        {"sender_id": sender["id"], "recipient_id": current_user["id"], "is_read": False},
        {"$set": {"is_read": True}}
    )
    return {"status": "success"}
