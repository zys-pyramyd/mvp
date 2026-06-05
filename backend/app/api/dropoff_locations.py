from fastapi import APIRouter, HTTPException, Depends
from app.api.deps import get_db, get_current_user
from app.models.order import DropoffLocationCreate, DropoffLocationUpdate
from typing import Optional
from datetime import datetime
import uuid

router = APIRouter()

ALLOWED_ROLES = ["agent", "farmer", "business"]


def _clean_location(loc: dict) -> dict:
    loc.pop("_id", None)
    for field in ("created_at", "updated_at"):
        if isinstance(loc.get(field), datetime):
            loc[field] = loc[field].isoformat()
    return loc


@router.post("")
async def create_dropoff_location(
    location_data: DropoffLocationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new drop-off location (agents and sellers only)."""
    if current_user.get("role") not in ALLOWED_ROLES:
        raise HTTPException(status_code=403, detail="Only agents and sellers can create drop-off locations")

    db = get_db()
    location = {
        "id": str(uuid.uuid4()),
        "name": location_data.name,
        "address": location_data.address,
        "city": location_data.city,
        "state": location_data.state,
        "country": location_data.country,
        "coordinates": location_data.coordinates,
        "contact_person": location_data.contact_person,
        "contact_phone": location_data.contact_phone,
        "operating_hours": location_data.operating_hours,
        "description": location_data.description,
        "agent_username": current_user["username"],
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    db.dropoff_locations.insert_one(location)

    return {
        "message": "Drop-off location created successfully",
        "location_id": location["id"],
        "location": {
            "id": location["id"],
            "name": location["name"],
            "address": location["address"],
            "city": location["city"],
            "state": location["state"],
        },
    }


@router.get("/states-cities")
async def get_dropoff_states_cities():
    """Get distinct states and cities from active drop-off locations."""
    db = get_db()
    states = list(db.dropoff_locations.distinct("state", {"is_active": True}))
    cities_by_state = {
        state: sorted(db.dropoff_locations.distinct("city", {"state": state, "is_active": True}))
        for state in states
    }
    return {"states": sorted(states), "cities_by_state": cities_by_state}


@router.get("/my-locations")
async def get_my_dropoff_locations(current_user: dict = Depends(get_current_user)):
    """Get the current user's created drop-off locations."""
    if current_user.get("role") not in ALLOWED_ROLES:
        raise HTTPException(status_code=403, detail="Only agents and sellers can view their drop-off locations")

    db = get_db()
    locations = list(
        db.dropoff_locations.find({"agent_username": current_user["username"]}).sort("created_at", -1)
    )
    return {"locations": [_clean_location(loc) for loc in locations], "total_count": len(locations)}


@router.get("")
async def get_dropoff_locations(
    state: Optional[str] = None,
    city: Optional[str] = None,
    active_only: bool = True,
    page: int = 1,
    limit: int = 50,
):
    """Get available drop-off locations with optional state/city filtering."""
    db = get_db()
    query: dict = {}
    if active_only:
        query["is_active"] = True
    if state:
        query["state"] = {"$regex": state, "$options": "i"}
    if city:
        query["city"] = {"$regex": city, "$options": "i"}

    total_count = db.dropoff_locations.count_documents(query)
    skip = (page - 1) * limit
    locations = list(
        db.dropoff_locations.find(query)
        .sort([("state", 1), ("city", 1), ("name", 1)])
        .skip(skip)
        .limit(limit)
    )
    return {
        "locations": [_clean_location(loc) for loc in locations],
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit,
    }


@router.get("/{location_id}")
async def get_dropoff_location(location_id: str):
    """Get details of a specific drop-off location."""
    db = get_db()
    location = db.dropoff_locations.find_one({"id": location_id})
    if not location or not location.get("is_active", False):
        raise HTTPException(status_code=404, detail="Drop-off location not found or inactive")
    return _clean_location(location)


@router.put("/{location_id}")
async def update_dropoff_location(
    location_id: str,
    location_data: DropoffLocationUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update a drop-off location (creator only)."""
    db = get_db()
    location = db.dropoff_locations.find_one({"id": location_id})
    if not location:
        raise HTTPException(status_code=404, detail="Drop-off location not found")
    if location["agent_username"] != current_user["username"]:
        raise HTTPException(status_code=403, detail="You can only update your own drop-off locations")

    update_data = {k: v for k, v in location_data.dict(exclude_unset=True).items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    db.dropoff_locations.update_one({"id": location_id}, {"$set": update_data})

    return {"message": "Drop-off location updated successfully"}


@router.delete("/{location_id}")
async def delete_dropoff_location(
    location_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Soft-delete (deactivate) a drop-off location (creator only)."""
    db = get_db()
    location = db.dropoff_locations.find_one({"id": location_id})
    if not location:
        raise HTTPException(status_code=404, detail="Drop-off location not found")
    if location["agent_username"] != current_user["username"]:
        raise HTTPException(status_code=403, detail="You can only delete your own drop-off locations")

    db.dropoff_locations.update_one(
        {"id": location_id},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}},
    )
    return {"message": "Drop-off location deactivated successfully"}
