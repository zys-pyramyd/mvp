"""
Database initialization and setup functions.

On every app startup:
  - Ensures all required MongoDB indexes exist (idempotent).

Admin creation is handled by the HTTP endpoint:
  POST /api/setup/create-admin
"""

import logging
from app.db.mongodb import get_db

logger = logging.getLogger(__name__)


def initialize_database():
    """
    Run all database initialization tasks on startup.
    Called automatically by FastAPI's startup event in app/main.py.
    """
    logger.info("Initializing database...")
    _ensure_indexes()
    logger.info("Database initialization complete.")


def _ensure_indexes():
    """
    Create all required MongoDB indexes. Idempotent — safe to call repeatedly.
    Mirrors the index list in app/api/setup.py::_build_indexes().
    """
    try:
        db = get_db()

        # orders
        db.orders.create_index([("status", 1), ("created_at", -1)])
        db.orders.create_index("buyer_username")
        db.orders.create_index("seller_id")
        db.orders.create_index("buyer_id")

        # users
        db.users.create_index("email", unique=True)
        db.users.create_index("id")

        # messages
        db.messages.create_index([("conversation_id", 1), ("created_at", -1)])

        # products
        db.products.create_index("id")
        db.products.create_index("community_id")
        db.products.create_index("seller_id")
        db.products.create_index("category")
        db.products.create_index([("is_active", 1), ("created_at", -1)])

        # communities
        db.communities.create_index("id")
        db.communities.create_index("is_private")
        db.communities.create_index("category")

        # community_members
        db.community_members.create_index("community_id")
        db.community_members.create_index("user_id")

        # community_posts
        db.community_posts.create_index([("community_id", 1), ("created_at", -1)])

        # rfq / offers
        db.rfq_orders.create_index("order_id")
        db.rfq_orders.create_index([("status", 1), ("created_at", -1)])
        db.offers.create_index("id")
        db.offers.create_index("buyer_id")

        # wallet_transactions
        db.wallet_transactions.create_index("user_id")
        db.wallet_transactions.create_index([("user_id", 1), ("created_at", -1)])

        # preorders
        db.preorders.create_index("id")
        db.preorders.create_index("buyer_id")
        db.preorders.create_index([("status", 1), ("created_at", -1)])

        # kyc_submissions
        db.kyc_submissions.create_index("user_id", unique=True)
        db.kyc_submissions.create_index("status")

        logger.info("MongoDB indexes verified/created successfully.")
    except Exception as e:
        # Don't crash startup — log and continue. The app is still functional.
        logger.error(f"Index creation error during startup (non-fatal): {e}")

