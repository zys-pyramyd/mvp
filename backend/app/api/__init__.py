
from fastapi import APIRouter
from app.api import auth, users, products, orders, admin, agent, paystack, upload
import app.api.admin_documents as admin_documents

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(users.user_router, prefix="/user", tags=["user"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(admin_documents.router, prefix="/admin", tags=["admin-documents"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(paystack.router, prefix="/paystack", tags=["paystack"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
import app.api.rfq as rfq
import app.api.communities as communities

api_router.include_router(communities.router, prefix="/communities", tags=["communities"])
api_router.include_router(rfq.router, prefix="/requests", tags=["rfq"])

from app.api import kyc
api_router.include_router(kyc.router, prefix="/kyc", tags=["kyc"])

