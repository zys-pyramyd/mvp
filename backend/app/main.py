

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.init_db import initialize_database
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# SECURITY: Rate limiting
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# SECURITY: CORS Configuration
# In production, replace with your actual domain
allowed_origins = [
    "https://pyramydhub.com",
    "https://www.pyramydhub.com",
    "http://localhost:3000",  # Development
    "http://localhost:3001",
]

if settings.BACKEND_CORS_ORIGINS:
    allowed_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # SECURITY: Specific origins only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup events
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("startup", initialize_database)
app.add_event_handler("shutdown", close_mongo_connection)

# Region verification and health scheduler
@app.on_event("startup")
def verify_region_and_start_scheduler():
    render_region = os.getenv("RENDER_SERVICE_REGION")
    mongo_region = os.getenv("MONGO_CLUSTER_REGION")
    if render_region and mongo_region and render_region != mongo_region:
        logging.warning(f"Render region ({render_region}) differs from MongoDB region ({mongo_region})")
    # Start health check scheduler to ping every 5 minutes
    scheduler = AsyncIOScheduler()
    scheduler.add_job(health_check, "interval", minutes=5)
    scheduler.start()

app.include_router(api_router, prefix="/api")

@app.get("/api/health")
async def health_check():
    try:
        from app.db.mongodb import db
        # Ping the MongoDB server
        db.client.admin.command('ping')
        return {"status": "healthy", "service": "Pyramyd API", "db": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "service": "Pyramyd API", "db": "error", "error": str(e)}

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
