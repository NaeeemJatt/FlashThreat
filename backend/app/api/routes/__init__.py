from fastapi import APIRouter

from app.api.routes import auth, ioc, providers

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(ioc.router, tags=["ioc"])
api_router.include_router(providers.router, tags=["providers"])

