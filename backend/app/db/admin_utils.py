import uuid
from datetime import datetime
import app.db.mongodb as mongodb

def create_admin_user(email: str, password_hash: str, first_name: str = "Pyramyd", last_name: str = "Admin", db_instance=None) -> None:
    """Create an admin user document and insert it into the users collection.
    This function is idempotent: if an admin with the given email already exists, it does nothing.
    """
    db = db_instance if db_instance is not None else mongodb.get_db()
    # Check for existing admin with same email
    if db.users.find_one({"email": email}):
        print(f"Admin with email {email} already exists, skipping creation")
        return
    admin_user = {
        "id": str(uuid.uuid4()),
        "first_name": first_name,
        "last_name": last_name,
        "username": email.split('@')[0],
        "email": email,
        "phone": "+234000000000",
        "password": password_hash,
        "role": "admin",
        "is_verified": True,
        "created_at": datetime.utcnow(),
        "profile_picture": None,
    }
    db.users.insert_one(admin_user)
    print(f"✅ Admin user {email} created (or already existed).")
