"""
Admin User Creation Script for Pyramyd Platform

This script creates an admin user directly in MongoDB.
Run this ONCE when setting up your production environment.

Usage:
    python create_admin.py

Requirements:
    - pymongo
    - bcrypt (or passlib)
    - Access to MongoDB connection string
"""

from pymongo import MongoClient
import bcrypt
import uuid
from datetime import datetime
import os

# MongoDB Connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017/")
DATABASE_NAME = "pyramyd"  # Change if different

def create_admin_user(email, password, first_name="Admin", last_name="User"):
    """
    Create an admin user in MongoDB
    
    Args:
        email: Admin email address
        password: Plain text password (will be hashed)
        first_name: Admin first name
        last_name: Admin last name
    """
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URL)
        db = client[DATABASE_NAME]
        
        # Check if admin already exists
        existing = db.users.find_one({"email": email})
        if existing:
            print(f"❌ User with email {email} already exists!")
            return False
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create admin user document
        admin_user = {
            "id": str(uuid.uuid4()),
            "first_name": first_name,
            "last_name": last_name,
            "username": email.split('@')[0],  # Use email prefix as username
            "email": email,
            "phone": "+234000000000",  # Placeholder
            "password": password_hash,
            "role": "admin",
            "is_verified": True,
            "created_at": datetime.utcnow(),
            "profile_picture": None
        }
        
        # Insert into database
        result = db.users.insert_one(admin_user)
        
        print("\n✅ Admin user created successfully!")
        print(f"📧 Email: {email}")
        print(f"👤 Username: {admin_user['username']}")
        print(f"🆔 User ID: {admin_user['id']}")
        print(f"\n🔐 Login with these credentials on your app's login page")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        return False
    finally:
        client.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Pyramyd Admin User Creation")
    print("=" * 60)
    
    # Get admin details
    print("\nEnter admin details:")
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    first_name = input("First Name (default: Admin): ").strip() or "Admin"
    last_name = input("Last Name (default: User): ").strip() or "User"
    
    # Validate inputs
    if not email or not password:
        print("❌ Email and password are required!")
        exit(1)
    
    if len(password) < 8:
        print("❌ Password must be at least 8 characters!")
        exit(1)
    
    # Confirm
    print(f"\n📝 Creating admin user:")
    print(f"   Email: {email}")
    print(f"   Name: {first_name} {last_name}")
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ Cancelled")
        exit(0)
    
    # Create admin
    create_admin_user(email, password, first_name, last_name)
