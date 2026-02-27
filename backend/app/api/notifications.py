from fastapi import APIRouter, HTTPException, Depends
from app.api.deps import get_db, get_current_user
from app.models.notification import Notification
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[Notification])
async def get_notifications(
    skip: int = 0, 
    limit: int = 50, 
    current_user: dict = Depends(get_current_user)
):
    """Get user notifications, newest first"""
    db = get_db()
    notifications = list(db.notifications.find(
        {"user_id": current_user['id']}
    ).sort("created_at", -1).skip(skip).limit(limit))
    
    return notifications

@router.get("/unread-count")
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    """Get count of unread notifications"""
    db = get_db()
    count = db.notifications.count_documents({
        "user_id": current_user['id'],
        "is_read": False
    })
    return {"count": count}

@router.post("/{notification_id}/read")
async def mark_as_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    """Mark a notification as read"""
    db = get_db()
    result = db.notifications.update_one(
        {"id": notification_id, "user_id": current_user['id']},
        {"$set": {"is_read": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    return {"message": "Marked as read"}

@router.post("/mark-all-read")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    """Mark all user notifications as read"""
    db = get_db()
    result = db.notifications.update_many(
        {"user_id": current_user['id'], "is_read": False},
        {"$set": {"is_read": True}}
    )
    
    return {"message": f"Marked {result.modified_count} notifications as read"}

# --- Internal Helper ---
def create_notification(user_id: str, title: str, message: str, type: str = "system", action_link: str = None):
    """
    Internal helper to create a notification. 
    Can be imported by other modules (kyc, orders, etc).
    """
    from app.db.mongodb import get_database # Avoid circular import of get_db dependency
    db = get_database()
    
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        action_link=action_link
    )
    
    try:
        db.notifications.insert_one(notification.dict())
        return True
    except Exception as e:
        print(f"Failed to create notification: {e}")
        return False
