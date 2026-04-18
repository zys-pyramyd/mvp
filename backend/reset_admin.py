from pymongo import MongoClient
import sys
import os

sys.path.insert(0, os.path.abspath('.'))
from app.core.security import hash_password

uri = "mongodb+srv://pyadmin_subset:dMnU9UZc93eC9qXf@cluster0.rdo4zru.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client.pyramyd

TARGET_EMAIL = "zyspyramyd@gmail.com"
NEW_PASSWORD = "AdminPassword123!"

admin = db.users.find_one({"email": TARGET_EMAIL, "role": "admin"})
if not admin:
    print(f"Admin {TARGET_EMAIL} not found.")
else:
    hashed = hash_password(NEW_PASSWORD)
    # CRITICAL: The db schema expects "password", NOT "hashed_password"
    db.users.update_one({"email": TARGET_EMAIL}, {"$set": {"password": hashed}, "$unset": {"hashed_password": ""}})
    print(f"Successfully fixed! Password for {TARGET_EMAIL} has been updated using the correct field name.")
