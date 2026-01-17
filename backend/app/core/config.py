
import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from .env file if present
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "Pyramyd Agritech"
    PROJECT_VERSION: str = "1.0.0"
    
    # Database
    MONGO_URL: str = os.environ.get("MONGO_URL", "mongodb://localhost:27017/")
    
    # Security
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "your-secret-key-here-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 hours
    ENCRYPTION_KEY: str = os.environ.get("ENCRYPTION_KEY")
    
    # External APIs
    PAYSTACK_SECRET_KEY: str = os.environ.get("PAYSTACK_SECRET_KEY", "sk_test_dummy_paystack_key")
    PAYSTACK_PUBLIC_KEY: str = os.environ.get("PAYSTACK_PUBLIC_KEY", "pk_test_dummy_paystack_key")
    PAYSTACK_API_URL: str = "https://api.paystack.co"
    
    TWILIO_SID: str = os.environ.get("TWILIO_ACCOUNT_SID", "dummy_twilio_sid")
    TWILIO_TOKEN: str = os.environ.get("TWILIO_AUTH_TOKEN", "dummy_twilio_token")
    
    KWIK_API_KEY: str = os.environ.get("KWIK_API_KEY", "dummy_kwik_key")
    KWIK_API_URL: str = "https://api.kwik.delivery/v1"
    
    # Business Logic
    FARMHUB_SPLIT_GROUP: str = os.environ.get("FARMHUB_SPLIT_GROUP", "SPL_dCqIOTFNRu")
    FARMHUB_SUBACCOUNT: str = os.environ.get("FARMHUB_SUBACCOUNT", "ACCT_c94r8ia2jeg41lx")
    
    # Admin
    ADMIN_EMAIL: str = os.environ.get("ADMIN_EMAIL", "admin@pyramydhub.com")
    ADMIN_PASSWORD: str = os.environ.get("ADMIN_PASSWORD", "admin123")
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [os.environ.get("FRONTEND_URL", "*"), "http://localhost:3000", "http://localhost:3001"]
    
    def __init__(self):
        # Allow comma-separated strings for CORS
        if isinstance(self.BACKEND_CORS_ORIGINS, list) and len(self.BACKEND_CORS_ORIGINS) == 1 and "," in self.BACKEND_CORS_ORIGINS[0]:
             self.BACKEND_CORS_ORIGINS = [origin.strip() for origin in self.BACKEND_CORS_ORIGINS[0].split(",")]

        # Critical: Encryption Key Handling
        if not self.ENCRYPTION_KEY:
            if os.environ.get("ENVIRONMENT") == "production":
                 raise ValueError("CRITICAL: ENCRYPTION_KEY is missing in production. Data processing will fail.")
            else:
                # Dev Only: Auto-generate with warning
                from cryptography.fernet import Fernet
                print("WARNING: Using auto-generated ENCRYPTION_KEY. Data will not persist across restarts.")
                self.ENCRYPTION_KEY = Fernet.generate_key().decode()

settings = Settings()
