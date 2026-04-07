# Auto-extracted Router
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.api.deps import get_db, get_current_user
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import random
import string

router = APIRouter()

@router.post("/api/messages/send")
async def send_message(
    message_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Send a message to another user"""
    db = get_db()
    try:
        # Validate message data
        if not message_data.get("recipient_username"):
            raise HTTPException(status_code=400, detail="Recipient username is required")
        
        if not message_data.get("content") and not message_data.get("audio_data"):
            raise HTTPException(status_code=400, detail="Message content or audio data is required")
        
        # Check if recipient exists
        recipient = users_collection.find_one({"username": message_data["recipient_username"]})
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found")
        
        # Create message document
        message = {
            "id": str(uuid.uuid4()),
            "sender_username": current_user["username"],
            "recipient_username": message_data["recipient_username"],
            "conversation_id": message_data.get("conversation_id"),
            "type": message_data.get("type", "text"),
            "content": message_data.get("content"),
            "audio_data": message_data.get("audio_data"),
            "timestamp": datetime.utcnow(),
            "read": False
        }
        
        # Store message in database
        messages_collection.insert_one(message)
        
        return {"message": "Message sent successfully", "message_id": message["id"]}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.get("/api/messages/unread-count")
async def get_unread_messages_count(current_user: dict = Depends(get_current_user)):
    """Count unread messages for current user"""
    db = get_db()
    try:
        count = messages_collection.count_documents({
            "recipient_username": current_user["username"],
            "read": False
        })
        return {"unread_count": count}
    except Exception as e:
        print(f"Error counting unread messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to count unread messages")

@router.get("/api/messages/conversations")
async def get_conversations(current_user: dict = Depends(get_current_user)):
    """Get user's conversations"""
    db = get_db()
    try:
        # Get all messages where user is sender or recipient
        messages = list(messages_collection.find({
            "$or": [
                {"sender_username": current_user["username"]},
                {"recipient_username": current_user["username"]}
            ]
        }).sort("timestamp", -1))
        
        # Group by conversation_id and get latest message for each
        conversations = {}
        for message in messages:
            conv_id = message.get("conversation_id")
            if conv_id and conv_id not in conversations:
                # Get the other participant
                other_user = message["recipient_username"] if message["sender_username"] == current_user["username"] else message["sender_username"]
                other_user_data = users_collection.find_one({"username": other_user}, {"password": 0})
                
                if other_user_data:
                    # Clean up other_user_data
                    other_user_data.pop('_id', None)
                    
                    # Clean up message for response
                    message_copy = message.copy()
                    message_copy.pop('_id', None)
                    message_copy["timestamp"] = message_copy["timestamp"].isoformat()
                    
                    conversations[conv_id] = {
                        "id": conv_id,
                        "participants": [current_user["username"], other_user],
                        "other_user": {
                            "username": other_user_data["username"],
                            "first_name": other_user_data.get("first_name", ""),
                            "last_name": other_user_data.get("last_name", "")
                        },
                        "last_message": message_copy,
                        "timestamp": message["timestamp"].isoformat()
                    }
        
        return list(conversations.values())
        
    except Exception as e:
        print(f"Error getting conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get conversations")

@router.get("/api/messages/{conversation_id}")
async def get_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get messages for a specific conversation"""
    db = get_db()
    try:
        # Get all messages for this conversation
        messages = list(messages_collection.find({
            "conversation_id": conversation_id,
            "$or": [
                {"sender_username": current_user["username"]},
                {"recipient_username": current_user["username"]}
            ]
        }).sort("timestamp", 1))
        
        # Clean up messages for response
        for message in messages:
            message.pop('_id', None)
            message["timestamp"] = message["timestamp"].isoformat()
        
        # Mark messages as read
        messages_collection.update_many(
            {
                "conversation_id": conversation_id,
                "recipient_username": current_user["username"],
                "read": False
            },
            {"$set": {"read": True}}
        )
        
        return messages
        
    except Exception as e:
        print(f"Error getting messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

