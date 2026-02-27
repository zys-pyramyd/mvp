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
    admin_user = {
        "id": str(uuid.uuid4()),
        "first_name": "Pyramyd",
        "last_name": "Admin",
        "username": "pyramyd_admin",
        "email": admin_email,
        "phone": "+234000000000",
        "password": admin_password_hash,
        "role": "admin",
        "is_verified": True,
        "created_at": datetime.utcnow(),
        "profile_picture": None
    }
    
    try:
        db.users.insert_one(admin_user)
        print("=" * 60)
        print("DEFAULT ADMIN USER CREATED")
        print("=" * 60)
        print(f"Email: {admin_email}")
        print(f"Username: pyramyd_admin")
        print(f"Password: [HIDDEN] (Use 'admin123' if default)")
        print("=" * 60)
        print("IMPORTANT: Change the password after first login!")
        print("=" * 60)
    except Exception as e:
        print(f"Error creating default admin: {str(e)}")


def initialize_database():
    """
    Run all database initialization tasks on startup
    """
    print("\nInitializing database...")
    create_default_admin()
    print("Database initialization complete\n")
