import os
import sys
from pydantic import EmailStr
import bcrypt
from pymongo import MongoClient
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def hash_password(password: str) -> str:
    # Use raw bcrypt just like app/core/security.py
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_admin():
    print("=======================================")
    print("    PYRAMYD - FIRST ADMIN GENERATOR    ")
    print("=======================================")
    
    # Get MongoDB Credentials
    MONGO_USERNAME = os.environ.get("MONGO_USERNAME")
    MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
    MONGO_CLUSTER = os.environ.get("MONGO_CLUSTER")
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "pyramyd")
    MONGO_AUTH_SOURCE = os.environ.get("MONGO_AUTH_SOURCE", "admin")

    if not all([MONGO_USERNAME, MONGO_PASSWORD, MONGO_CLUSTER]):
        print("❌ Error: Missing MongoDB credentials in your .env file.")
        print("Please ensure MONGO_USERNAME, MONGO_PASSWORD, and MONGO_CLUSTER are set.")
        sys.exit(1)

    # Build Connection String
    encoded_password = urllib.parse.quote_plus(MONGO_PASSWORD)
    if "mongodb.net" in MONGO_CLUSTER:
        mongo_url = f"mongodb+srv://{MONGO_USERNAME}:{encoded_password}@{MONGO_CLUSTER}/?authSource={MONGO_AUTH_SOURCE}&retryWrites=true&w=majority&appName=Pyramyd"
    else:
        mongo_url = f"mongodb://{MONGO_USERNAME}:{encoded_password}@{MONGO_CLUSTER}/?authSource={MONGO_AUTH_SOURCE}"

    print("Connecting to MongoDB Atlas...")
    try:
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client[MONGO_DB_NAME]
        print("Connected successfully!")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    # Check if admin already exists
    if db.users.find_one({"role": "admin"}):
        print("An admin user already exists in the database.")
        choice = input("Do you want to create another one? (y/n): ")
        if choice.lower() != 'y':
            sys.exit(0)

    # Gather Admin Details
    print("\n--- Enter Admin Details ---")
    first_name = input("First Name: ").strip()
    last_name = input("Last Name: ").strip()
    email = input("Email Address: ").strip()
    
    # Simple validation
    if not email or "@" not in email:
        print("Invalid email format.")
        sys.exit(1)
        
    # Check if email exists
    if db.users.find_one({"email": email}):
        print(f"A user with email {email} already exists!")
        sys.exit(1)
        
    password = input("Password (min 8 chars, 1 uppercase, 1 digit): ").strip()

    print("\nGenerating admin account...")
    
    import uuid
    from datetime import datetime
    
    # Use shared admin creation utility
    try:
        from app.db.admin_utils import create_admin_user
        create_admin_user(email, hash_password(password), first_name, last_name, db_instance=db)
        print("Role: Admin")
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    seed_admin()
