"""
Database initialization and setup functions
Creates default admin user on first startup
"""

from app.db.mongodb import get_db
from app.core.config import settings
import uuid
from datetime import datetime


# Admin creation has been moved to the production seed script (scripts/seed_admin.py).


def initialize_database():
    """
    Run all database initialization tasks on startup
    """
    print("\nInitializing database...")
    # create_default_admin()  # Skipped – handled by seed_admin script
    print("Database initialization complete\n")
