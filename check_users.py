
import os
from pymongo import MongoClient

# Use the connection string from server.py (or default)
MONGO_URL = os.environ.get('MONGO_URI', os.environ.get('MONGO_URL', 'mongodb://localhost:27017/'))

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db = client['pyramyd']
    users = list(db.users.find({}, {"email": 1, "role": 1, "username": 1, "_id": 0}))
    
    print(f"Found {len(users)} users:")
    for user in users:
        print(f"- {user.get('email', 'N/A')} ({user.get('username', 'N/A')}): {user.get('role', 'N/A')}")

except Exception as e:
    print(f"Error: {e}")
