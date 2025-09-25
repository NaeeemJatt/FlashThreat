# FlashThreat API Documentation

## Overview

FlashThreat provides a comprehensive REST API for threat intelligence analysis. The API allows you to check Indicators of Compromise (IOCs) against multiple threat intelligence providers and retrieve detailed analysis results.

## Base URL

```
http://localhost:8000/api
```

## Authentication

FlashThreat uses JWT-based authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

## Rate Limiting

The API implements rate limiting to prevent abuse:
- **60 requests per minute** per IP address
- **1000 requests per hour** per IP address

Rate limit information is included in response headers:
- `X-RateLimit-Limit-Minute`: Requests allowed per minute
- `X-RateLimit-Remaining-Minute`: Remaining requests this minute
- `X-RateLimit-Limit-Hour`: Requests allowed per hour
- `X-RateLimit-Remaining-Hour`: Remaining requests this hour

## Endpoints

### Authentication

#### POST /auth/login
Login and get access token.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### GET /auth/me
Get current user information.

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "analyst"
}
```

### IOC Analysis

#### POST /check_ioc
Check an IOC against all providers.

**Request Body:**
```json
{
  "ioc": "8.8.8.8",
  "force_refresh": false
}
```

**Response:**
```json
{
  "lookup_id": "uuid",
  "ioc": "8.8.8.8",
  "ioc_type": "ipv4",
  "providers": [
    {
      "provider": "virustotal",
      "status": "ok",
      "latency_ms": 500,
      "reputation": 10,
      "malicious_count": 0,
      "harmless_count": 50,
      "evidence": [...]
    }
  ],
  "summary": {
    "verdict": "clean",
    "score": 10,
    "explanation": "Low threat score from all providers"
  },
  "timing": {
    "total_ms": 1500
  }
}
```

#### GET /stream_ioc
Stream IOC check results in real-time.

**Query Parameters:**
- `ioc`: IOC to check
- `force_refresh`: Whether to force refresh cache (default: false)
- `show_raw`: Include raw API responses (default: false)

**Response:** Server-Sent Events stream

#### GET /lookup/{lookup_id}
Get lookup results by ID.

**Response:**
```json
{
  "id": "uuid",
  "ioc": {
    "id": "uuid",
    "value": "8.8.8.8",
    "type": "ipv4"
  },
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "analyst"
  },
  "started_at": "2023-09-22T10:00:00Z",
  "finished_at": "2023-09-22T10:00:01Z",
  "score": 10,
  "verdict": "clean",
  "provider_results": [...],
  "notes": [...]
}
```

### Bulk Processing

#### POST /bulk
Submit bulk IOC check job.

**Request:** Multipart form data with CSV file

**Response:**
```json
{
  "job_id": "uuid",
  "status": "pending",
  "total_iocs": 100,
  "message": "Bulk job submitted successfully"
}
```

#### GET /bulk/{job_id}
Get bulk job status and results.

**Response:**
```json
{
  "id": "uuid",
  "status": "completed",
  "total_iocs": 100,
  "processed_iocs": 100,
  "completed_iocs": 95,
  "failed_iocs": 5,
  "results": [...]
}
```

### System Monitoring

#### GET /providers/health
Get system health status.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2023-09-22T10:00:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection successful"
    },
    "providers": {
      "virustotal": {
        "status": "healthy",
        "message": "Provider available"
      }
    }
  }
}
```

#### GET /providers/metrics
Get application metrics.

**Query Parameters:**
- `hours`: Number of hours to look back (default: 24)

**Response:**
```json
{
  "period_hours": 24,
  "timestamp": "2023-09-22T10:00:00Z",
  "total_requests": 1500,
  "requests_by_status": {
    "200": 1400,
    "400": 50,
    "500": 10
  },
  "requests_by_endpoint": {
    "/api/check_ioc": 800,
    "/api/stream_ioc": 300
  },
  "error_rate": 4.0
}
```

#### GET /providers/performance
Get detailed performance metrics.

**Response:**
```json
{
  "timestamp": "2023-09-22T10:00:00Z",
  "system_metrics": {
    "system": {
      "memory": {
        "percent": 45.2,
        "threshold_exceeded": false
      },
      "cpu": {
        "percent": 25.5
      }
    },
    "process": {
      "memory": {
        "rss": 150000000
      },
      "cpu": 15.2
    }
  },
  "performance_health": {
    "status": "healthy",
    "issues": [],
    "recommendations": []
  }
}
```

## Error Handling

All errors follow a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "type": "ErrorType"
  }
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Request validation failed
- `IOC_VALIDATION_ERROR`: Invalid IOC format
- `PROVIDER_ERROR`: External provider error
- `CACHE_ERROR`: Cache operation failed
- `DATABASE_ERROR`: Database operation failed
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded
- `AUTHENTICATION_ERROR`: Authentication failed
- `AUTHORIZATION_ERROR`: Insufficient permissions

## Security Headers

All responses include security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'; ...`

## Examples

### Check an IP Address
```bash
curl -X POST "http://localhost:8000/api/check_ioc" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"ioc": "8.8.8.8", "force_refresh": false}'
```

### Stream IOC Results
```bash
curl -N "http://localhost:8000/api/stream_ioc?ioc=google.com" \
  -H "Authorization: Bearer <token>"
```

### Get System Health
```bash
curl "http://localhost:8000/api/providers/health" \
  -H "Authorization: Bearer <token>"
```

## SDK Examples

### Python
```python
import httpx

async def check_ioc(ioc: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/check_ioc",
            json={"ioc": ioc, "force_refresh": False},
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

### JavaScript
```javascript
async function checkIOC(ioc, token) {
  const response = await fetch('/api/check_ioc', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ ioc, force_refresh: false })
  });
  return await response.json();
}
```

## Rate Limiting Examples

### Check Rate Limit Status
```bash
curl -I "http://localhost:8000/api/providers/health"
```

Response headers will show:
```
X-RateLimit-Limit-Minute: 60
X-RateLimit-Remaining-Minute: 59
X-RateLimit-Limit-Hour: 1000
X-RateLimit-Remaining-Hour: 999
```

### Handle Rate Limiting
```python
import httpx
import time

async def make_request_with_retry(client, url, max_retries=3):
    for attempt in range(max_retries):
        response = await client.get(url)
        
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited. Retrying after {retry_after} seconds...")
            time.sleep(retry_after)
            continue
        
        return response
    
    raise Exception("Max retries exceeded")
```
