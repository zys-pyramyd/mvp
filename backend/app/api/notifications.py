from fastapi import APIRouter, HTTPException, Depends
from app.api.deps import get_db, get_current_user
from app.models.notification import Notification
from typing import List, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[Notification])
async def get_notifications(
    skip: int = 0, 
    limit: int = 50, 
    current_user: dict = Depends(get_current_user)
):
    """Get user notifications, newest first."""
    db = get_db()
    # Platform admins also receive role-broadcast notifications
    query = {"$or": [{"user_id": current_user['id']}]}
    if current_user.get('role') == 'admin':
        query["$or"].append({"recipient_role": "platform_admin"})

    notifications = list(
        db.notifications.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    for n in notifications:
        n.pop('_id', None)
    return notifications


@router.get("/unread-count")
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    """Get count of unread notifications."""
    db = get_db()
    query = {"$or": [{"user_id": current_user['id'], "is_read": False}]}
    if current_user.get('role') == 'admin':
        query["$or"].append({"recipient_role": "platform_admin", "is_read": False})
    count = db.notifications.count_documents(query)
    return {"count": count}


@router.post("/{notification_id}/read")
async def mark_as_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    """Mark a notification as read."""
    db = get_db()
    result = db.notifications.update_one(
        {"id": notification_id},
        {"$set": {"is_read": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Marked as read"}


@router.post("/mark-all-read")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    """Mark all user notifications as read."""
    db = get_db()
    query = {"$or": [{"user_id": current_user['id'], "is_read": False}]}
    if current_user.get('role') == 'admin':
        query["$or"].append({"recipient_role": "platform_admin", "is_read": False})
    result = db.notifications.update_many(query, {"$set": {"is_read": True}})
    return {"message": f"Marked {result.modified_count} notifications as read"}


# ---------------------------------------------------------------------------
# Internal Helpers
# These are imported by other modules (kyc.py, auth.py, agent.py, etc.)
# ---------------------------------------------------------------------------

def create_notification(
    user_id: str,
    title: str,
    message: str,
    type: str = "system",
    action_link: Optional[str] = None
) -> bool:
    """
    Create a notification for a SPECIFIC USER by their user_id.
    Use this for user-directed messages (KYC result, order update, etc.).
    Do NOT pass user_id='admin' — use notify_platform_admins() for admin alerts.
    """
    try:
        from app.api.deps import get_db as _get_db
        db = _get_db()
        doc = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "recipient_role": None,  # individual delivery
            "title": title,
            "message": message,
            "type": type,
            "action_link": action_link,
            "is_read": False,
            "created_at": datetime.utcnow()
        }
        db.notifications.insert_one(doc)
        return True
    except Exception as e:
        logger.error(f"Failed to create notification for user {user_id}: {e}")
        return False


def notify_platform_admins(
    title: str,
    message: str,
    type: str = "system",
    action_link: Optional[str] = None
) -> bool:
    """
    Broadcast a notification to ALL platform administrators (role='admin').
    This is SEPARATE from community group admins (creator_role in community_members).

    Use this instead of create_notification(user_id='admin') which was an anti-pattern.
    Delivered to every user whose platform role is 'admin'.
    """
    try:
        from app.api.deps import get_db as _get_db
        db = _get_db()
        doc = {
            "id": str(uuid.uuid4()),
            "user_id": None,           # not for a specific user
            "recipient_role": "platform_admin",  # broadcast to all platform admins
            "title": title,
            "message": message,
            "type": type,
            "action_link": action_link,
            "is_read": False,
            "created_at": datetime.utcnow()
        }
        db.notifications.insert_one(doc)
        logger.info(f"[ADMIN NOTIFY] '{title}' broadcast to all platform admins")
        return True
    except Exception as e:
        logger.error(f"Failed to broadcast admin notification: {e}")
        return False

