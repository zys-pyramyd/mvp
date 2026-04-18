import os
from pymongo import MongoClient

# Extract from .env normally, but hardcoded here for testing
uri = "mongodb+srv://pyadmin_subset:dMnU9UZc93eC9qXf@cluster0.rdo4zru.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client.pyramyd

admin = db.users.find_one({"role": "admin"})
if admin:
    print(f"Admin exists! Email: {admin.get('email')} | Username: {admin.get('username')}")
else:
    print("No admin user found in database.")

users = db.users.find().limit(5)
print("Some users:")
for u in users:
    print(f"- {u.get('email')} ({u.get('role')})")
