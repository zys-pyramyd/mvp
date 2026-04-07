"""
Database initialization and setup functions
Creates default admin user on first startup
"""

from app.db.mongodb import get_db
from app.core.config import settings
import uuid
from datetime import datetime


def create_default_admin():
    """
    Create default admin user if no admin exists.
    Uses credentials from environment variables.
    """
    db = get_db()
    
    # Check if any admin user exists
    existing_admin = db.users.find_one({"role": "admin"})
    if existing_admin:
        print("Admin user already exists, skipping creation")
        return
    
    # Get admin credentials from environment
    admin_email = settings.ADMIN_EMAIL
    admin_password_hash = settings.ADMIN_PASSWORD_HASH
    
    # Create default admin user
    # Create default admin user using shared utility
    try:
        from .admin_utils import create_admin_user
        create_admin_user(admin_email, admin_password_hash, first_name="Pyramyd", last_name="Admin")
    except Exception as e:
        print(f"Error creating default admin: {str(e)}")


def initialize_database():
    """
    Run all database initialization tasks on startup
    """
    print("\nInitializing database...")
    create_default_admin()
    print("Database initialization complete\n")
