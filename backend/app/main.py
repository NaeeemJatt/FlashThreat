from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.middleware.rate_limit import rate_limit_middleware
from app.middleware.error_handler import error_handler_middleware
from app.middleware.security import security_headers
from app.middleware.metrics import metrics_middleware

# Create FastAPI app
app = FastAPI(
    title="FlashThreat",
    description="FlashThreat - Advanced threat intelligence analysis platform",
    version="0.1.0",
)

# Add middleware (order matters - error handler should be first)
app.middleware("http")(error_handler_middleware)
app.middleware("http")(metrics_middleware)
app.middleware("http")(rate_limit_middleware)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint."""
    from fastapi import Response
    
    response_data = {
        "message": "Welcome to FlashThreat API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }
    
    # Add security headers
    response = Response(content=str(response_data), media_type="application/json")
    for header, value in security_headers.get_security_headers().items():
        response.headers[header] = value
    
    return response


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

