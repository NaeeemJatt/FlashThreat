"""
Performance tests for FlashThreat API.
"""
import asyncio
import time
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestPerformance:
    """Performance tests for the FlashThreat API."""
    
    @pytest.mark.asyncio
    async def test_api_response_time(self, client: AsyncClient, db: AsyncSession):
        """Test API response times are within acceptable limits."""
        start_time = time.time()
        
        response = await client.get("/api/providers/health")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Health check should respond within 1 second
        assert response_time < 1.0
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_ioc_check_performance(self, client: AsyncClient, db: AsyncSession):
        """Test IOC check performance."""
        test_ioc = "8.8.8.8"
        
        start_time = time.time()
        
        response = await client.post(
            "/api/check_ioc",
            json={"ioc": test_ioc, "force_refresh": False}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # IOC check should complete within 10 seconds
        assert response_time < 10.0
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client: AsyncClient, db: AsyncSession):
        """Test handling of concurrent requests."""
        test_iocs = ["8.8.8.8", "1.1.1.1", "google.com", "example.com"]
        
        start_time = time.time()
        
        # Make concurrent requests
        tasks = []
        for ioc in test_iocs:
            task = client.post(
                "/api/check_ioc",
                json={"ioc": ioc, "force_refresh": False}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All requests should complete within 15 seconds
        assert total_time < 15.0
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_database_query_performance(self, client: AsyncClient, db: AsyncSession):
        """Test database query performance."""
        start_time = time.time()
        
        response = await client.get("/api/history?limit=50&offset=0")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # History query should complete within 2 seconds
        assert response_time < 2.0
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_memory_usage(self, client: AsyncClient, db: AsyncSession):
        """Test memory usage doesn't grow excessively."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Make multiple requests
        for i in range(10):
            response = await client.get("/api/providers/health")
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (less than 10MB)
        assert memory_growth < 10 * 1024 * 1024
    
    @pytest.mark.asyncio
    async def test_rate_limiting_performance(self, client: AsyncClient, db: AsyncSession):
        """Test rate limiting doesn't significantly impact performance."""
        start_time = time.time()
        
        # Make requests up to the rate limit
        responses = []
        for i in range(60):  # Just under the 60 req/min limit
            response = await client.get("/api/providers/health")
            responses.append(response)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time
        assert total_time < 30.0
        
        # Most requests should succeed (some might be rate limited)
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 50  # At least 50 should succeed
