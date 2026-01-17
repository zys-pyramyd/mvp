
import bcrypt
import jwt
from datetime import datetime, timedelta
from app.core.config import settings

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=30) # Default to 30 days
        # We could use settings.JWT_EXPIRATION_MINUTES here
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

# Encryption
from cryptography.fernet import Fernet

cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode() if isinstance(settings.ENCRYPTION_KEY, str) else settings.ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    if not data:
        return None
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return None
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        print(f"Decryption error: {str(e)}")
        return None
