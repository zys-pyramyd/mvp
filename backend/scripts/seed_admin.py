import os
import sys
from pymongo import MongoClient

# Try to import password hashing utility from the app, fallback to passlib if unavailable.
try:
    from app.core.security import get_password_hash
except ImportError:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)


def bootstrap_admin():
    """Create the initial admin user in a production MongoDB deployment.
    This script is intended to be run once (e.g. during CI/CD or a manual
    bootstrap step) after the service is deployed.
    """
    # 1. Grab variables from the environment (Render, Docker, etc.)
    mongo_uri = os.getenv("MONGODB_URI")
    admin_email = os.getenv("INITIAL_ADMIN_EMAIL")
    admin_password = os.getenv("INITIAL_ADMIN_PASSWORD")
    db_name = os.getenv("MONGODB_DB_NAME", "pyramyd_db")

    if not all([mongo_uri, admin_email, admin_password]):
        print("❌ Missing required environment variables (MONGODB_URI, INITIAL_ADMIN_EMAIL, INITIAL_ADMIN_PASSWORD).")
        return

    try:
        # 2. Connect to MongoDB (synchronous driver works for a one‑off script)
        client = MongoClient(mongo_uri)
        db = client[db_name]
        users_collection = db["users"]  # Adjust if your collection name differs

        # 3. Check if the admin already exists
        existing_admin = users_collection.find_one({"email": admin_email})
        if existing_admin:
            print(f"ℹ️ Admin {admin_email} already exists. Skipping creation.")
            return

        print(f"🚀 Creating admin: {admin_email}...")
        # 4. Build the admin document – keys must match the app's user model
        admin_doc = {
            "email": admin_email,
            "hashed_password": get_password_hash(admin_password),
            "is_admin": True,
            "is_active": True,
            "role": "admin",
            "created_at": "__system_bootstrap__",
        }
        users_collection.insert_one(admin_doc)
        print("✅ Admin created successfully in MongoDB.")
    except Exception as e:
        print(f"❌ Connection error or insertion failed: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    bootstrap_admin()
