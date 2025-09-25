"""
Error handling middleware for FastAPI.
"""
import logging
import traceback
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class FlashThreatException(Exception):
    """Base exception for FlashThreat application."""
    
    def __init__(self, message: str, error_code: str = None, status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class IOCValidationError(FlashThreatException):
    """Exception for IOC validation errors."""
    
    def __init__(self, message: str, ioc_value: str = None):
        super().__init__(
            message=message,
            error_code="IOC_VALIDATION_ERROR",
            status_code=400
        )
        self.ioc_value = ioc_value


class ProviderError(FlashThreatException):
    """Exception for provider-related errors."""
    
    def __init__(self, message: str, provider: str = None):
        super().__init__(
            message=message,
            error_code="PROVIDER_ERROR",
            status_code=503
        )
        self.provider = provider


class CacheError(FlashThreatException):
    """Exception for cache-related errors."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            status_code=503
        )


async def error_handler_middleware(request: Request, call_next):
    """
    Global error handling middleware.
    
    Args:
        request: FastAPI request
        call_next: Next middleware/handler
        
    Returns:
        JSON response with error details
    """
    try:
        response = await call_next(request)
        return response
        
    except FlashThreatException as e:
        logger.error(f"FlashThreat error: {e.message}", extra={
            "error_code": e.error_code,
            "status_code": e.status_code,
            "path": request.url.path,
            "method": request.method,
        })
        
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": {
                    "code": e.error_code,
                    "message": e.message,
                    "type": "FlashThreatError"
                }
            }
        )
        
    except HTTPException as e:
        logger.warning(f"HTTP error: {e.detail}", extra={
            "status_code": e.status_code,
            "path": request.url.path,
            "method": request.method,
        })
        
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": e.detail,
                    "type": "HTTPException"
                }
            }
        )
        
    except RequestValidationError as e:
        logger.warning(f"Validation error: {e.errors()}", extra={
            "path": request.url.path,
            "method": request.method,
        })
        
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": e.errors(),
                    "type": "ValidationError"
                }
            }
        )
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}", extra={
            "path": request.url.path,
            "method": request.method,
        })
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "Database operation failed",
                    "type": "DatabaseError"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc(),
        })
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "type": "InternalError"
                }
            }
        )


def create_error_response(
    message: str,
    error_code: str = "UNKNOWN_ERROR",
    status_code: int = 500,
    details: dict = None
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        error_code: Error code
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        JSONResponse with error details
    """
    content = {
        "error": {
            "code": error_code,
            "message": message,
            "type": "Error"
        }
    }
    
    if details:
        content["error"]["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )
