
from fastapi import APIRouter
from app.api import auth, users, products, orders, admin, agent, paystack

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(users.user_router, prefix="/user", tags=["user"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(paystack.router, prefix="/paystack", tags=["paystack"])
import app.api.rfq as rfq
import app.api.communities as communities

api_router.include_router(rfq.router, prefix="/requests", tags=["rfq"])
api_router.include_router(communities.router, prefix="/communities", tags=["communities"])

