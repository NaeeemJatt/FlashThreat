import pytest
import respx
from fastapi import status
from httpx import AsyncClient, Response

from app.core.config import settings


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test the root endpoint."""
    response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "Welcome" in response.json()["message"]


@pytest.mark.asyncio
@respx.mock
async def test_check_ioc_endpoint(client: AsyncClient):
    """Test the check_ioc endpoint."""
    # Mock provider responses
    respx.get(
        f"{settings.PROVIDERS_CONFIG.virustotal.base_url}/ip_addresses/8.8.8.8"
    ).respond(
        status_code=200,
        json={"data": {"attributes": {"last_analysis_stats": {"malicious": 0}}}}
    )
    
    respx.get(
        f"{settings.PROVIDERS_CONFIG.abuseipdb.base_url}/check"
    ).respond(
        status_code=200,
        json={"data": {"abuseConfidenceScore": 0}}
    )
    
    respx.get(
        f"{settings.PROVIDERS_CONFIG.shodan.base_url}/shodan/host/8.8.8.8"
    ).respond(
        status_code=200,
        json={"country_name": "United States"}
    )
    
    respx.get(
        f"{settings.PROVIDERS_CONFIG.otx.base_url}/indicators/IPv4/8.8.8.8/general"
    ).respond(
        status_code=200,
        json={"pulse_info": {"count": 0}}
    )
    
    # Test the endpoint
    response = await client.post("/api/check_ioc", json={"ioc": "8.8.8.8"})
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Check basic structure
    assert "ioc" in data
    assert "summary" in data
    assert "providers" in data
    assert "timing" in data
    assert "lookup_id" in data
    
    # Check IOC data
    assert data["ioc"]["value"] == "8.8.8.8"
    assert data["ioc"]["type"] == "ipv4"
    
    # Check summary
    assert "verdict" in data["summary"]
    assert "score" in data["summary"]
    assert "explanation" in data["summary"]
    
    # Check providers
    assert len(data["providers"]) > 0
    for provider in data["providers"]:
        assert "provider" in provider
        assert "status" in provider


@pytest.mark.asyncio
@respx.mock
async def test_check_ioc_invalid(client: AsyncClient):
    """Test the check_ioc endpoint with invalid IOC."""
    response = await client.post("/api/check_ioc", json={"ioc": "invalid"})
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "error" in data
    assert data["error"] == "Invalid IOC format"


@pytest.mark.asyncio
@respx.mock
async def test_stream_ioc_endpoint(client: AsyncClient):
    """Test the stream_ioc endpoint."""
    # Mock provider responses
    respx.get(
        f"{settings.PROVIDERS_CONFIG.virustotal.base_url}/ip_addresses/8.8.8.8"
    ).respond(
        status_code=200,
        json={"data": {"attributes": {"last_analysis_stats": {"malicious": 0}}}}
    )
    
    # Test the endpoint
    response = await client.get("/api/stream_ioc?ioc=8.8.8.8")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "text/event-stream"
    
    # Check that the response contains event data
    content = response.content.decode()
    assert "event: " in content
    assert "data: " in content


@pytest.mark.asyncio
async def test_get_providers_endpoint(client: AsyncClient):
    """Test the get_providers endpoint."""
    response = await client.get("/api/providers")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "providers" in data
    assert len(data["providers"]) > 0
    
    for provider in data["providers"]:
        assert "name" in provider
        assert "supports_types" in provider


@pytest.mark.asyncio
async def test_get_health_endpoint(client: AsyncClient):
    """Test the get_health endpoint."""
    response = await client.get("/api/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "status" in data
    assert data["status"] == "ok"

