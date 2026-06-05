from fastapi import APIRouter, HTTPException, Depends
from app.api.deps import get_db, get_current_user
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class TrackingUpdate(BaseModel):
    status: str
    location: Optional[str] = None
    note: Optional[str] = None


@router.get("/{tracking_id}", tags=["Tracking"])
async def get_public_tracking(tracking_id: str):
    """
    Public endpoint: Get order tracking history.
    Stripped of sensitive user data.
    """
    db = get_db()
    log = db.tracking_logs.find_one({"tracking_id": tracking_id})
    if not log:
        raise HTTPException(status_code=404, detail="Tracking ID not found")

    return {
        "tracking_id": log["tracking_id"],
        "status": log["current_status"],
        "logs": log.get("logs", []),
        "estimated_delivery": log.get("estimated_delivery"),
    }


@router.post("/{tracking_id}/update", tags=["Tracking"])
async def update_tracking_log(
    tracking_id: str,
    update: TrackingUpdate,
    current_user: dict = Depends(get_current_user),
):
    """
    Restricted: Agents/Admins update tracking status.
    """
    db = get_db()
    if current_user["role"] not in ["agent", "admin", "logistics"]:
        raise HTTPException(status_code=403, detail="Not authorized to update tracking")

    log = db.tracking_logs.find_one({"tracking_id": tracking_id})
    if not log:
        raise HTTPException(status_code=404, detail="Tracking ID not found")

    new_entry = {
        "status": update.status,
        "location": update.location,
        "note": update.note,
        "updated_by": current_user["username"],
        "timestamp": datetime.utcnow().isoformat(),
    }

    db.tracking_logs.update_one(
        {"tracking_id": tracking_id},
        {
            "$push": {"logs": new_entry},
            "$set": {"current_status": update.status},
        },
    )

    return {"status": "success", "message": "Tracking updated"}
