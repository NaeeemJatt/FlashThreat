"""
Security tests for FlashThreat API.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestSecurity:
    """Security tests for the FlashThreat API."""
    
    @pytest.mark.asyncio
    async def test_xss_protection(self, client: AsyncClient, db: AsyncSession):
        """Test XSS protection in input sanitization."""
        # Test various XSS payloads
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<iframe src=javascript:alert('xss')></iframe>",
            "<object data=javascript:alert('xss')></object>",
            "<embed src=javascript:alert('xss')></embed>",
            "<link rel=stylesheet href=javascript:alert('xss')>",
            "<meta http-equiv=refresh content=0;url=javascript:alert('xss')>",
            "<style>@import'javascript:alert(\"xss\")';</style>",
            "expression(alert('xss'))",
            "url(javascript:alert('xss'))",
            "@import url('javascript:alert(\"xss\")')",
        ]
        
        for payload in xss_payloads:
            response = await client.post(
                "/api/check_ioc",
                json={"ioc": payload, "force_refresh": False}
            )
            
            # Should either reject the input or sanitize it
            if response.status_code == 400:
                # Input was rejected (good)
                assert "malicious input" in response.json().get("error", {}).get("message", "").lower()
            elif response.status_code == 200:
                # Input was accepted but should be sanitized
                data = response.json()
                # The IOC should be sanitized (no script tags, etc.)
                assert "<script>" not in str(data)
                assert "javascript:" not in str(data)
    
    @pytest.mark.asyncio
    async def test_sql_injection_protection(self, client: AsyncClient, db: AsyncSession):
        """Test SQL injection protection."""
        # Test various SQL injection payloads
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "' OR 1=1 --",
            "'; EXEC xp_cmdshell('dir'); --",
            "' OR 1=1; EXEC sp_configure 'show advanced options', 1; --",
        ]
        
        for payload in sql_payloads:
            response = await client.post(
                "/api/check_ioc",
                json={"ioc": payload, "force_refresh": False}
            )
            
            # Should either reject the input or handle it safely
            if response.status_code == 400:
                # Input was rejected (good)
                assert "malicious input" in response.json().get("error", {}).get("message", "").lower()
            elif response.status_code == 200:
                # Input was accepted but should be handled safely
                # The database should not be compromised
                pass
    
    @pytest.mark.asyncio
    async def test_rate_limiting_security(self, client: AsyncClient, db: AsyncSession):
        """Test rate limiting prevents abuse."""
        # Make many requests quickly
        responses = []
        for i in range(100):
            response = await client.get("/api/providers/health")
            responses.append(response)
            
            # Stop if we get rate limited
            if response.status_code == 429:
                break
        
        # Should eventually get rate limited
        rate_limited_responses = [r for r in responses if r.status_code == 429]
        assert len(rate_limited_responses) > 0, "Rate limiting should be triggered"
        
        # Check rate limit headers
        rate_limited_response = rate_limited_responses[0]
        assert "X-RateLimit-Limit-Minute" in rate_limited_response.headers
        assert "X-RateLimit-Remaining-Minute" in rate_limited_response.headers
        assert "Retry-After" in rate_limited_response.headers
    
    @pytest.mark.asyncio
    async def test_input_validation_security(self, client: AsyncClient, db: AsyncSession):
        """Test input validation prevents malicious data."""
        # Test extremely long inputs
        long_input = "A" * 10000
        response = await client.post(
            "/api/check_ioc",
            json={"ioc": long_input, "force_refresh": False}
        )
        
        # Should reject extremely long inputs
        assert response.status_code == 400
        
        # Test null bytes and control characters
        malicious_inputs = [
            "\x00\x01\x02\x03",  # Null bytes and control characters
            "test\x00injection",  # Null byte injection
            "test\x1ainjection",  # Control character
            "test\xffinjection",  # Invalid UTF-8
        ]
        
        for malicious_input in malicious_inputs:
            response = await client.post(
                "/api/check_ioc",
                json={"ioc": malicious_input, "force_refresh": False}
            )
            
            # Should handle malicious inputs safely
            assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_authentication_security(self, client: AsyncClient, db: AsyncSession):
        """Test authentication security measures."""
        # Test without authentication
        response = await client.get("/api/auth/me")
        assert response.status_code == 401
        
        # Test with invalid token
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        
        # Test with malformed token
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "InvalidFormat token"}
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_headers_security(self, client: AsyncClient, db: AsyncSession):
        """Test security headers are properly set."""
        response = await client.get("/")
        
        # Check security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        
        for header, expected_value in security_headers.items():
            assert header in response.headers
            assert response.headers[header] == expected_value
        
        # Check Content Security Policy
        assert "Content-Security-Policy" in response.headers
        csp = response.headers["Content-Security-Policy"]
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp
    
    @pytest.mark.asyncio
    async def test_path_traversal_protection(self, client: AsyncClient, db: AsyncSession):
        """Test path traversal protection."""
        # Test path traversal attempts
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc//passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        ]
        
        for payload in path_traversal_payloads:
            response = await client.get(f"/api/lookup/{payload}")
            
            # Should handle path traversal attempts safely
            assert response.status_code in [400, 404]
    
    @pytest.mark.asyncio
    async def test_json_injection_protection(self, client: AsyncClient, db: AsyncSession):
        """Test JSON injection protection."""
        # Test JSON injection payloads
        json_payloads = [
            '{"ioc": "test", "malicious": "value"}',
            '{"ioc": "test", "__proto__": {"polluted": true}}',
            '{"ioc": "test", "constructor": {"prototype": {"polluted": true}}}',
        ]
        
        for payload in json_payloads:
            response = await client.post(
                "/api/check_ioc",
                content=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Should handle JSON injection safely
            assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_csrf_protection(self, client: AsyncClient, db: AsyncSession):
        """Test CSRF protection."""
        # Test with missing CSRF token (if implemented)
        response = await client.post(
            "/api/check_ioc",
            json={"ioc": "8.8.8.8", "force_refresh": False},
            headers={"Origin": "https://malicious-site.com"}
        )
        
        # Should handle cross-origin requests appropriately
        # (This depends on CORS configuration)
        assert response.status_code in [200, 403]
