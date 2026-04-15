"""
Setup endpoints for one-time platform bootstrapping.

These endpoints are meant to be called ONCE after initial deployment
on platforms like Render where shell access is unavailable (free tier).

Security model:
  - All endpoints require a correct `setup_secret` matching the
    ADMIN_SETUP_SECRET environment variable.
  - Admin creation additionally checks that no admin user already exists,
    making it effectively self-disabling after first use.
  - These endpoints are safe to leave in permanently — the secret is the gate.

Usage after deploying to Render:
  POST /api/setup/create-admin   — Create the first admin account
  POST /api/setup/create-indexes — Ensure all MongoDB indexes exist
"""

import os
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, validator

from app.core.security import hash_password
from app.api.deps import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class CreateAdminSetupRequest(BaseModel):
    """
    Only the setup secret is required in the request body.
    Admin credentials (name, email, password) are read from environment
    variables set in your Render dashboard — never sent over the wire.
    """
    setup_secret: str


class CreateIndexesRequest(BaseModel):
    setup_secret: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _verify_setup_secret(provided: str) -> None:
    """Raise 403 if the provided secret doesn't match ADMIN_SETUP_SECRET."""
    expected = os.environ.get("ADMIN_SETUP_SECRET", "")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "ADMIN_SETUP_SECRET is not configured on this server. "
                "Add it to your Render environment variables first."
            ),
        )
    if provided != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid setup secret. Access denied.",
        )


def _build_indexes(db) -> dict:
    """
    Create all required MongoDB indexes.  MongoDB's create_index is
    idempotent — calling it when the index already exists is a no-op.
    Returns a summary dict suitable for returning as an API response.
    """
    created = {}

    # ---- orders ----
    db.orders.create_index([("status", 1), ("created_at", -1)])
    db.orders.create_index("buyer_username")
    db.orders.create_index("seller_id")
    db.orders.create_index("buyer_id")
    created["orders"] = ["status+created_at", "buyer_username", "seller_id", "buyer_id"]

    # ---- users ----
    db.users.create_index("email", unique=True)
    db.users.create_index("id")
    created["users"] = ["email (unique)", "id"]

    # ---- messages ----
    db.messages.create_index([("conversation_id", 1), ("created_at", -1)])
    created["messages"] = ["conversation_id+created_at"]

    # ---- products ----
    db.products.create_index("id")
    db.products.create_index("community_id")
    db.products.create_index("seller_id")
    db.products.create_index("category")
    db.products.create_index([("is_active", 1), ("created_at", -1)])
    created["products"] = ["id", "community_id", "seller_id", "category", "is_active+created_at"]

    # ---- communities ----
    db.communities.create_index("id")
    db.communities.create_index("is_private")
    db.communities.create_index("category")
    created["communities"] = ["id", "is_private", "category"]

    # ---- community_members ----
    db.community_members.create_index("community_id")
    db.community_members.create_index("user_id")
    created["community_members"] = ["community_id", "user_id"]

    # ---- community_posts ----
    db.community_posts.create_index([("community_id", 1), ("created_at", -1)])
    created["community_posts"] = ["community_id+created_at"]

    # ---- rfq / offers ----
    db.rfq_orders.create_index("order_id")
    db.rfq_orders.create_index([("status", 1), ("created_at", -1)])
    db.offers.create_index("id")
    db.offers.create_index("buyer_id")
    created["rfq_orders"] = ["order_id", "status+created_at"]
    created["offers"] = ["id", "buyer_id"]

    # ---- wallet_transactions ----
    db.wallet_transactions.create_index("user_id")
    db.wallet_transactions.create_index([("user_id", 1), ("created_at", -1)])
    created["wallet_transactions"] = ["user_id", "user_id+created_at"]

    # ---- preorders ----
    db.preorders.create_index("id")
    db.preorders.create_index("buyer_id")
    db.preorders.create_index([("status", 1), ("created_at", -1)])
    created["preorders"] = ["id", "buyer_id", "status+created_at"]

    # ---- kyc_submissions ----
    db.kyc_submissions.create_index("user_id", unique=True)
    db.kyc_submissions.create_index("status")
    created["kyc_submissions"] = ["user_id (unique)", "status"]

    return created


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/create-admin",
    status_code=status.HTTP_201_CREATED,
    summary="Bootstrap the first platform admin (no JWT required)",
    tags=["setup"],
)
async def create_first_admin(request: CreateAdminSetupRequest):
    """
    Create the very first admin user for the Pyramyd platform.

    **Call this endpoint once after your first deployment on Render.**

    Admin credentials are read from environment variables — you only need
    to send `{ "setup_secret": "your_secret" }` in the request body:

    Required env vars (set in Render dashboard):
      - ADMIN_SETUP_SECRET   — guards this endpoint
      - ADMIN_FIRST_NAME     — admin's first name
      - ADMIN_LAST_NAME      — admin's last name
      - ADMIN_EMAIL          — admin login email
      - ADMIN_PASSWORD       — admin login password (min 8 chars, 1 upper, 1 digit)

    - Returns 409 if any admin already exists (self-disabling after first use).
    - No JWT token required — there wouldn't be one yet!
    """
    _verify_setup_secret(request.setup_secret)

    # Read admin credentials from environment — never from the request body
    first_name = os.environ.get("ADMIN_FIRST_NAME", "").strip()
    last_name  = os.environ.get("ADMIN_LAST_NAME",  "").strip()
    email      = os.environ.get("ADMIN_EMAIL",       "").strip()
    password   = os.environ.get("ADMIN_PASSWORD",    "").strip()

    # Validate all required env vars are present
    missing = [name for name, val in [
        ("ADMIN_FIRST_NAME", first_name),
        ("ADMIN_LAST_NAME",  last_name),
        ("ADMIN_EMAIL",      email),
        ("ADMIN_PASSWORD",   password),
    ] if not val]

    if missing:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Set them in your Render dashboard and redeploy, then call this endpoint again."
            ),
        )

    # Validate password complexity
    pwd_errors = []
    if len(password) < 8:
        pwd_errors.append("at least 8 characters")
    if not any(c.isupper() for c in password):
        pwd_errors.append("at least one uppercase letter")
    if not any(c.islower() for c in password):
        pwd_errors.append("at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        pwd_errors.append("at least one digit")
    if pwd_errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"ADMIN_PASSWORD must contain: {', '.join(pwd_errors)}.",
        )

    db = get_db()

    # Safety gate: only allow creation if no admin exists yet
    existing_admin = db.users.find_one({"role": "admin"})
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An admin user already exists. "
                "Use POST /api/admin/users/create (with your admin JWT) to add more admins."
            ),
        )

    # Email uniqueness check
    if db.users.find_one({"email": email}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A user with email '{email}' already exists.",
        )

    import uuid
    admin_doc = {
        "id": str(uuid.uuid4()),
        "first_name": first_name,
        "last_name":  last_name,
        "username":   email.split("@")[0],
        "email":      email,
        "phone":      None,
        "password":   hash_password(password),
        "role":       "admin",
        "is_verified": True,
        "kyc_status":  "approved",
        "wallet_balance": 0.0,
        "profile_picture": None,
        "created_at": datetime.utcnow(),
    }

    db.users.insert_one(admin_doc)
    logger.info(f"[SETUP] First admin account created: {email}")

    return {
        "message": "Admin user created successfully. You can now log in via the frontend.",
        "email": email,
        "username": admin_doc["username"],
        "hint": (
            "This endpoint is now self-locked — it returns 409 on any future call. "
            "Use POST /api/admin/users/create to add more admins."
        ),
    }


@router.post(
    "/create-indexes",
    status_code=status.HTTP_200_OK,
    summary="Create / ensure all MongoDB indexes exist",
    tags=["setup"],
)
async def create_indexes(request: CreateIndexesRequest):
    """
    Ensure all required MongoDB indexes exist.

    **Safe to call at any time — it is fully idempotent.**

    Indexes are also created automatically on every app startup,
    so you typically only need to call this manually if you want
    to verify or force-refresh them.

    Requires `setup_secret` matching the `ADMIN_SETUP_SECRET` env var.
    """
    _verify_setup_secret(request.setup_secret)

    db = get_db()

    try:
        created = _build_indexes(db)
        logger.info("[SETUP] MongoDB indexes created/verified successfully.")
        return {
            "message": "All indexes created (or already existed).",
            "indexes": created,
        }
    except Exception as e:
        logger.error(f"[SETUP] Index creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Index creation failed: {str(e)}",
        )
