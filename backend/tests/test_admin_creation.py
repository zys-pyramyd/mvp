import sys, os
# Ensure the project root is on the import path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bcrypt
from app.db.admin_utils import create_admin_user
from app.db import mongodb

# Simple in‑memory fake DB for testing
class _FakeCollection:
    def __init__(self):
        self._data = []
    def delete_many(self, filter):
        self._data = [doc for doc in self._data if not all(doc.get(k) == v for k, v in filter.items())]
    def find_one(self, filter):
        for doc in self._data:
            if all(doc.get(k) == v for k, v in filter.items()):
                return doc
        return None
    def insert_one(self, doc):
        self._data.append(doc)
    def find(self, filter):
        return [doc for doc in self._data if all(doc.get(k) == v for k, v in filter.items())]

class _FakeDB:
    def __init__(self):
        self.users = _FakeCollection()

# Monkey‑patch the get_db function used by admin_utils
_fake_db = _FakeDB()
mongodb.get_db = lambda: _fake_db

def test_create_admin_idempotent():
    db = mongodb.get_db()
    # Ensure a clean state
    db.users.delete_many({"role": "admin"})

    email = "testadmin@example.com"
    password = "StrongPass123!"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # First creation
    create_admin_user(email, password_hash, first_name="Test", last_name="Admin")
    admin = db.users.find_one({"email": email})
    assert admin is not None
    assert admin["role"] == "admin"

    # Second creation should be idempotent (no duplicate)
    create_admin_user(email, password_hash, first_name="Test", last_name="Admin")
    admins = db.users.find({"email": email})
    assert len(admins) == 1
