"""
Security middleware for input sanitization and XSS protection.
"""
import re
import html
from typing import Any, Dict, List, Union
from fastapi import Request
from pydantic import BaseModel, validator


class SecuritySanitizer:
    """Security sanitizer for input validation and XSS protection."""
    
    # XSS patterns to detect and block
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
        r'<link[^>]*>',
        r'<meta[^>]*>',
        r'<style[^>]*>',
        r'expression\s*\(',
        r'url\s*\(',
        r'@import',
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'union\s+select',
        r'drop\s+table',
        r'delete\s+from',
        r'insert\s+into',
        r'update\s+set',
        r'exec\s*\(',
        r'execute\s*\(',
        r'--',
        r'/\*.*?\*/',
        r'xp_',
        r'sp_',
    ]
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """
        Sanitize a string input.
        
        Args:
            value: Input string
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
            
        Raises:
            ValueError: If input contains malicious patterns
        """
        if not isinstance(value, str):
            return str(value)
        
        # Check length
        if len(value) > max_length:
            raise ValueError(f"Input too long. Maximum length: {max_length}")
        
        # Check for XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Potentially malicious input detected")
        
        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Potentially malicious input detected")
        
        # HTML escape
        sanitized = html.escape(value, quote=True)
        
        # Remove any remaining HTML tags
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        return sanitized.strip()
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize a dictionary recursively.
        
        Args:
            data: Dictionary to sanitize
            
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize key
            sanitized_key = cls.sanitize_string(str(key), max_length=100)
            
            # Sanitize value
            if isinstance(value, str):
                sanitized[sanitized_key] = cls.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[sanitized_key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[sanitized_key] = cls.sanitize_list(value)
            else:
                sanitized[sanitized_key] = value
        
        return sanitized
    
    @classmethod
    def sanitize_list(cls, data: List[Any]) -> List[Any]:
        """
        Sanitize a list recursively.
        
        Args:
            data: List to sanitize
            
        Returns:
            Sanitized list
        """
        sanitized = []
        
        for item in data:
            if isinstance(item, str):
                sanitized.append(cls.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(cls.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(cls.sanitize_list(item))
            else:
                sanitized.append(item)
        
        return sanitized
    
    @classmethod
    def validate_ioc_input(cls, ioc: str) -> str:
        """
        Validate and sanitize IOC input.
        
        Args:
            ioc: IOC value to validate
            
        Returns:
            Sanitized IOC value
            
        Raises:
            ValueError: If IOC is invalid or malicious
        """
        if not ioc or not isinstance(ioc, str):
            raise ValueError("IOC value is required")
        
        # Basic length check
        if len(ioc) > 1000:
            raise ValueError("IOC value too long")
        
        # Check for malicious patterns
        sanitized = cls.sanitize_string(ioc, max_length=1000)
        
        # Additional IOC-specific validation
        if not re.match(r'^[a-zA-Z0-9\.\-\_\/\:\@\#\?\%\&\=\+]+$', sanitized):
            raise ValueError("IOC contains invalid characters")
        
        return sanitized


class SecurityHeaders:
    """Security headers for HTTP responses."""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """
        Get security headers for HTTP responses.
        
        Returns:
            Dictionary of security headers
        """
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'"
            ),
        }


# Global sanitizer instance
security_sanitizer = SecuritySanitizer()
security_headers = SecurityHeaders()
