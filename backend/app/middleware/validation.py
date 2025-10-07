"""
Input validation middleware for FastAPI.
"""
import re
from typing import Any, Dict, List, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.middleware.security import SecuritySanitizer


class InputValidator:
    """Input validation middleware."""
    
    def __init__(self):
        self.sanitizer = SecuritySanitizer()
    
    def validate_ioc_input(self, ioc: str) -> str:
        """
        Validate and sanitize IOC input.
        
        Args:
            ioc: IOC value to validate
            
        Returns:
            Sanitized IOC value
            
        Raises:
            HTTPException: If IOC is invalid
        """
        try:
            return self.sanitizer.validate_ioc_input(ioc)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_IOC",
                        "message": str(e),
                        "type": "ValidationError"
                    }
                }
            )
    
    def validate_file_upload(self, filename: str, content: bytes) -> None:
        """
        Validate file upload.
        
        Args:
            filename: Name of the uploaded file
            content: File content
            
        Raises:
            HTTPException: If file is invalid
        """
        # Check filename
        if not filename:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_FILENAME",
                        "message": "Filename is required",
                        "type": "ValidationError"
                    }
                }
            )
        
        # Check file extension
        if not filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_FILE_TYPE",
                        "message": "Only CSV files are allowed",
                        "type": "ValidationError"
                    }
                }
            )
        
        # Check file size
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "EMPTY_FILE",
                        "message": "File cannot be empty",
                        "type": "ValidationError"
                    }
                }
            )
        
        if len(content) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "FILE_TOO_LARGE",
                        "message": "File size exceeds 10MB limit",
                        "type": "ValidationError"
                    }
                }
            )
        
        # Check CSV content
        try:
            first_line = content.split(b'\n')[0].decode('utf-8', errors='ignore')
            if ',' not in first_line and '\t' not in first_line:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": {
                            "code": "INVALID_CSV_CONTENT",
                            "message": "File does not appear to be a valid CSV",
                            "type": "ValidationError"
                        }
                    }
                )
        except Exception:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_FILE_CONTENT",
                        "message": "Unable to read file content",
                        "type": "ValidationError"
                    }
                }
            )
    
    def validate_pagination(self, limit: int, offset: int) -> None:
        """
        Validate pagination parameters.
        
        Args:
            limit: Number of items per page
            offset: Number of items to skip
            
        Raises:
            HTTPException: If pagination parameters are invalid
        """
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_LIMIT",
                        "message": "Limit must be between 1 and 100",
                        "type": "ValidationError"
                    }
                }
            )
        
        if offset < 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_OFFSET",
                        "message": "Offset must be non-negative",
                        "type": "ValidationError"
                    }
                }
            )


# Global validator instance
input_validator = InputValidator()
