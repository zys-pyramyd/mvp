from cryptography.fernet import Fernet
import os

# Encryption Setup
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"WARNING: Using auto-generated encryption key. Set ENCRYPTION_KEY in production!")

cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    if not data:
        return None
    try:
        return cipher_suite.encrypt(str(data).encode()).decode()
    except Exception as e:
        print(f"Encryption error: {str(e)}")
        return None

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return None
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        print(f"Decryption error: {str(e)}")
        return None
