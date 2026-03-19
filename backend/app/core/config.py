
import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from .env file only in development (non‑production)
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if os.getenv("ENVIRONMENT") != "production":
    load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "Pyramyd Agritech"
    PROJECT_VERSION: str = "1.0.0"
    
    import urllib.parse
    
    # Environment variables for MongoDB
    MONGO_USERNAME: str = os.environ.get("MONGO_USERNAME", "")
    MONGO_PASSWORD: str = os.environ.get("MONGO_PASSWORD", "")
    MONGO_CLUSTER: str = os.environ.get("MONGO_CLUSTER")
    MONGO_DB_NAME: str = os.environ.get("MONGO_DB_NAME", "pyramyd")
    MONGO_AUTH_SOURCE: str = os.environ.get("MONGO_AUTH_SOURCE", "admin")
    
    # Generate MONGO_URL dynamically
    if MONGO_USERNAME and MONGO_PASSWORD:
        encoded_password = urllib.parse.quote_plus(MONGO_PASSWORD)
        # Use srv format if it's atlas/remote
        if "mongodb.net" in MONGO_CLUSTER:
            MONGO_URL: str = f"mongodb+srv://{MONGO_USERNAME}:{encoded_password}@{MONGO_CLUSTER}/?authSource={MONGO_AUTH_SOURCE}&retryWrites=true&w=majority&appName=Pyramyd"
        else:
            MONGO_URL: str = f"mongodb://{MONGO_USERNAME}:{encoded_password}@{MONGO_CLUSTER}/?authSource={MONGO_AUTH_SOURCE}"
    else:
        # Fallback to direct URL or localhost
        MONGO_URL: str = os.environ.get("MONGO_URL", f"mongodb://{MONGO_CLUSTER}/")
    
    # Security
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "your-secret-key-here-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 hours
    ENCRYPTION_KEY: str = os.environ.get("ENCRYPTION_KEY")
    
    # External APIs
    PAYSTACK_SECRET_KEY: str = os.environ.get("PAYSTACK_SECRET_KEY", "sk_test_dummy_paystack_key")
    PAYSTACK_PUBLIC_KEY: str = os.environ.get("PAYSTACK_PUBLIC_KEY", "pk_test_dummy_paystack_key")
    PAYSTACK_API_URL: str = "https://api.paystack.co"
    
    # Render overrides for production
    if os.environ.get("ENVIRONMENT") == "production":
        if PAYSTACK_SECRET_KEY == "sk_test_dummy_paystack_key":
            print("WARNING: Using DUMMY Paystack Secret Key in PRODUCTION! Payments will fail.")
    
    TWILIO_SID: str = os.environ.get("TWILIO_ACCOUNT_SID", "dummy_twilio_sid")
    TWILIO_TOKEN: str = os.environ.get("TWILIO_AUTH_TOKEN", "dummy_twilio_token")
    
    KWIK_API_KEY: str = os.environ.get("KWIK_API_KEY", "dummy_kwik_key")
    KWIK_API_URL: str = "https://api.kwik.delivery/v1"
    
    # Business Logic
    FARMHUB_SPLIT_GROUP: str = os.environ.get("FARMHUB_SPLIT_GROUP", "SPL_dCqIOTFNRu")
    FARMHUB_SUBACCOUNT: str = os.environ.get("FARMHUB_SUBACCOUNT", "ACCT_c94r8ia2jeg41lx")
    
    # Admin
    ADMIN_EMAIL: str = os.environ.get("ADMIN_EMAIL", "admin@pyramydhub.com")
    ADMIN_PASSWORD_HASH: str = os.environ.get("ADMIN_PASSWORD_HASH", "$2b$12$9O44mlAapYPMR81xvcyBhOHUYkD2vNPy./jp6Bf3HM/8PHY3QCR9i")
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [os.environ.get("FRONTEND_URL", "https://pyramydhub.com"), "https://pyramydhub.com", "https://www.pyramydhub.com", "http://localhost:3000", "http://localhost:3001"]
    
    def __init__(self):
        # Allow comma-separated strings for CORS
        if isinstance(self.BACKEND_CORS_ORIGINS, list) and len(self.BACKEND_CORS_ORIGINS) == 1 and "," in self.BACKEND_CORS_ORIGINS[0]:
             self.BACKEND_CORS_ORIGINS = [origin.strip() for origin in self.BACKEND_CORS_ORIGINS[0].split(",")]

        # Critical: Encryption Key Handling
        if not self.ENCRYPTION_KEY:
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError("CRITICAL: ENCRYPTION_KEY is missing in production. Data processing will fail.")
            else:
                # Dev Only: Auto-generate with warning
                from cryptography.fernet import Fernet
                print("WARNING: Using auto-generated ENCRYPTION_KEY. Data will not persist across restarts.")
                self.ENCRYPTION_KEY = Fernet.generate_key().decode()

        # Production validation for required MongoDB variables
        if os.getenv("ENVIRONMENT") == "production":
            required_vars = ["MONGO_USERNAME", "MONGO_PASSWORD", "MONGO_CLUSTER"]
            missing = [var for var in required_vars if not getattr(self, var)]
            if missing:
                raise ValueError(f"Missing required env vars for production: {', '.join(missing)}")

settings = Settings()
