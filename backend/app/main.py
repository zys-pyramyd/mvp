

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.init_db import initialize_database
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
    "http://localhost:3000",  # Development
    "http://localhost:3001",
    # Add production domains here:
    # "https://yourdomain.com",
    # "https://www.yourdomain.com",
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

app.include_router(api_router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Pyramyd API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
