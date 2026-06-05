import os
import uuid
import logging
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# App-specific imports
from database import db, init_db_indexes, ping_db
from app.core.rate_limit import limiter
from app.api import api_router
from app.services.payout_service import process_order_payout
from auth import get_password_hash

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- App Instantiation ---
app = FastAPI(title="Pyramyd API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS middleware ---
default_origins = "https://pyramydhub.com,https://www.pyramydhub.com,http://localhost:3000,http://localhost:3001"
origins_str = os.environ.get("ALLOWED_ORIGINS", default_origins)
origins = [origin.strip() for origin in origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Background Jobs ---
async def check_for_overdue_orders():
    """
    Background job to check for orders held in escrow 
    that are overdue for auto-confirmation (e.g. 10 days rule).
    Auto-confirms if delivered but not confirmed by buyer.
    """
    logger.info("Running auto-release checker...")
    try:
        now = datetime.utcnow()
        instant_cutoff = now - timedelta(days=3)   # PyExpress / Instant
        standard_cutoff = now - timedelta(days=14) # Farm Deals / Standard
        
        candidates = list(db.orders.find({
            "status": "delivered_pending_confirmation",
            "payout_halted": {"$ne": True} # Do not process halted orders
        }))
        
        for order in candidates:
            delivered_at = order.get('delivered_at')
            if not delivered_at: continue
                
            platform = order.get('platform')
            should_release = False
            
            if platform == 'pyexpress':
                if delivered_at < instant_cutoff:
                    should_release = True
            else: # farm_deals or others
                if delivered_at < standard_cutoff:
                    should_release = True
            
            if should_release:
                logger.info(f"Auto-release triggered for order {order.get('order_id')}")
                try:
                    db.orders.update_one(
                        {"order_id": order['order_id']}, 
                        {"$set": {"status": "completed", "auto_released": True, "completed_at": now}}
                    )
                    await process_order_payout(order['order_id'], db)
                except Exception as e:
                    logger.error(f"Failed to auto-process order {order.get('order_id')}: {e}")
    except Exception as e:
        logger.error(f"Error in auto-release job: {e}")

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    logger.info(f"Application starting up on port {os.environ.get('PORT', '8001')}...")
    
    # 1. Initialize DB Indexes
    init_db_indexes()
    
    # 2. Start Scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_for_overdue_orders, "interval", hours=1)
    scheduler.start()
    logger.info("APScheduler started for Auto-Release jobs.")

    # 3. Seed Admin User
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    
    if admin_email and admin_password:
        try:
            logger.info(f"Checking Admin User: {admin_email}")
            hashed_pw = get_password_hash(admin_password)
            existing_admin = db.users.find_one({"email": admin_email})
            
            if existing_admin:
                db.users.update_one(
                    {"email": admin_email},
                    {"$set": {"password": hashed_pw, "role": "admin"}}
                )
                logger.info("Admin password updated from environment variable.")
            else:
                new_admin = {
                    "id": str(uuid.uuid4()),
                    "email": admin_email,
                    "username": "admin",
                    "role": "admin",
                    "password": hashed_pw,
                    "is_verified": True,
                    "kyc_status": "verified",
                    "created_at": datetime.utcnow()
                }
                db.users.insert_one(new_admin)
                logger.info("New admin user created.")
        except Exception as e:
            logger.error(f"Failed to seed admin: {e}")

# --- Root Endpoints ---
@app.get("/")
async def root():
    return {"status": "ok", "message": "Pyramyd Backend Running", "service": "backend"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint for Render/Docker deployment monitoring."""
    db_healthy = ping_db()
    status = "healthy" if db_healthy else "degraded"
    return {
        "status": status,
        "database": "connected" if db_healthy else "disconnected",
        "service": "pyramyd-backend"
    }

# --- Include Modular Routes ---
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8001")))
