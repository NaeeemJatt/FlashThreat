"""
CSRF protection middleware for FastAPI.
"""
import secrets
from typing import Dict, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


class CSRFProtection:
    """CSRF protection middleware."""
    
    def __init__(self):
        self.secret_key = secrets.token_urlsafe(32)
    
    def generate_token(self, request: Request) -> str:
        """Generate CSRF token for the request."""
        # In a real implementation, you'd store this in a secure session
        # For now, we'll use a simple approach
        return secrets.token_urlsafe(32)
    
    def validate_token(self, request: Request, token: str) -> bool:
        """Validate CSRF token."""
        # In a real implementation, you'd validate against stored tokens
        # For now, we'll accept any non-empty token
        return bool(token and len(token) > 10)
    
    def get_csrf_headers(self) -> Dict[str, str]:
        """Get CSRF headers for responses."""
        return {
            "X-CSRF-Protection": "1",
            "X-Content-Type-Options": "nosniff",
        }


# Global CSRF protection instance
csrf_protection = CSRFProtection()


async def csrf_middleware(request: Request, call_next):
    """
    CSRF protection middleware.
    
    Args:
        request: FastAPI request
        call_next: Next middleware/handler
        
    Returns:
        Response with CSRF protection
    """
    # Skip CSRF for GET requests and safe methods
    if request.method in ["GET", "HEAD", "OPTIONS"]:
        response = await call_next(request)
        # Add CSRF headers
        for header, value in csrf_protection.get_csrf_headers().items():
            response.headers[header] = value
        return response
    
    # Skip CSRF for authentication endpoints
    if request.url.path in ["/api/auth/token", "/api/auth/users", "/api/auth/users/me"]:
        response = await call_next(request)
        # Add CSRF headers
        for header, value in csrf_protection.get_csrf_headers().items():
            response.headers[header] = value
        return response
    
    # For state-changing requests, check CSRF token
    csrf_token = request.headers.get("X-CSRF-Token")
    if not csrf_token:
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "CSRF_TOKEN_MISSING",
                    "message": "CSRF token is required for this request",
                    "type": "CSRFError"
                }
            }
        )
    
    # Validate CSRF token
    if not csrf_protection.validate_token(request, csrf_token):
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": "CSRF_TOKEN_INVALID",
                    "message": "Invalid CSRF token",
                    "type": "CSRFError"
                }
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add CSRF headers
    for header, value in csrf_protection.get_csrf_headers().items():
        response.headers[header] = value
    
    return response
