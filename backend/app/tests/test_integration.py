"""
Integration tests for FlashThreat API.
"""
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.tests.conftest import app


class TestIntegration:
    """Integration tests for the FlashThreat API."""
    
    @pytest.mark.asyncio
    async def test_full_ioc_check_flow(self, client: AsyncClient, db: AsyncSession):
        """Test complete IOC check flow from request to response."""
        # Test data
        test_ioc = "8.8.8.8"
        
        # Step 1: Check IOC
        response = await client.post(
            "/api/check_ioc",
            json={"ioc": test_ioc, "force_refresh": False}
        )
        
        # Should return 200 with result
        assert response.status_code == 200
        data = response.json()
        assert "lookup_id" in data
        assert "providers" in data
        assert "summary" in data
        
        # Step 2: Get lookup by ID
        lookup_id = data["lookup_id"]
        response = await client.get(f"/api/lookup/{lookup_id}")
        
        # Should return 200 with lookup details
        assert response.status_code == 200
        lookup_data = response.json()
        assert lookup_data["id"] == lookup_id
        assert "ioc" in lookup_data
        assert "provider_results" in lookup_data
    
    @pytest.mark.asyncio
    async def test_streaming_ioc_check(self, client: AsyncClient, db: AsyncSession):
        """Test streaming IOC check functionality."""
        test_ioc = "google.com"
        
        # Test streaming endpoint
        response = await client.get(
            f"/api/stream_ioc?ioc={test_ioc}&force_refresh=false"
        )
        
        # Should return streaming response
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
    
    @pytest.mark.asyncio
    async def test_health_check_integration(self, client: AsyncClient, db: AsyncSession):
        """Test health check endpoint with all components."""
        response = await client.get("/api/providers/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have health status
        assert "status" in data
        assert "timestamp" in data
        assert "components" in data
        
        # Should check database
        assert "database" in data["components"]
        assert "redis" in data["components"]
        assert "providers" in data["components"]
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, client: AsyncClient, db: AsyncSession):
        """Test metrics collection and retrieval."""
        # Make some requests to generate metrics
        await client.get("/api/providers/health")
        await client.get("/api/providers")
        
        # Get metrics
        response = await client.get("/api/providers/metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have metrics data
        assert "total_requests" in data
        assert "requests_by_status" in data
        assert "requests_by_endpoint" in data
        assert "error_rate" in data
    
    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, client: AsyncClient, db: AsyncSession):
        """Test rate limiting functionality."""
        # Make multiple requests quickly to trigger rate limiting
        responses = []
        for i in range(65):  # Exceed the 60 req/min limit
            response = await client.get("/api/providers/health")
            responses.append(response)
        
        # Should eventually get rate limited
        rate_limited = any(r.status_code == 429 for r in responses)
        assert rate_limited, "Rate limiting should be triggered"
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, client: AsyncClient, db: AsyncSession):
        """Test error handling across the application."""
        # Test invalid IOC
        response = await client.post(
            "/api/check_ioc",
            json={"ioc": "invalid_ioc_format", "force_refresh": False}
        )
        
        # Should handle error gracefully
        assert response.status_code in [400, 422]
        data = response.json()
        assert "error" in data
        
        # Test invalid lookup ID
        response = await client.get("/api/lookup/invalid-uuid")
        assert response.status_code == 400
        
        # Test non-existent lookup
        response = await client.get("/api/lookup/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_security_headers(self, client: AsyncClient, db: AsyncSession):
        """Test security headers are present."""
        response = await client.get("/")
        
        # Check security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
    
    @pytest.mark.asyncio
    async def test_cors_headers(self, client: AsyncClient, db: AsyncSession):
        """Test CORS headers are properly set."""
        response = await client.options("/api/providers/health")
        
        # Should have CORS headers
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers
