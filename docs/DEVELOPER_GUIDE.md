# FlashThreat Developer Guide

## Architecture Overview

FlashThreat is built with a modern, scalable architecture using FastAPI (Python) for the backend and React (JavaScript) for the frontend.

### Backend Architecture

```
backend/
├── app/
│   ├── api/routes/          # API endpoints
│   ├── core/               # Core configuration and utilities
│   ├── db/                 # Database configuration
│   ├── middleware/         # Custom middleware
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   └── services/          # Business logic
├── alembic/               # Database migrations
└── tests/                # Test suite
```

### Frontend Architecture

```
frontend/
├── src/
│   ├── components/       # React components
│   ├── pages/            # Page components
│   ├── lib/              # Utilities and API client
│   └── tests/            # Test suite
└── public/               # Static assets
```

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+
- Docker & Docker Compose (optional)

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd backend
   pip install poetry
   poetry install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Initialize database:**
   ```bash
   python init_db.py
   ```

4. **Run development server:**
   ```bash
   python run_server.py
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

## API Development

### Adding New Endpoints

1. **Create route file** in `app/api/routes/`
2. **Define endpoint** with proper typing
3. **Add to router** in `app/api/routes/__init__.py`
4. **Write tests** in `app/tests/`

Example:
```python
# app/api/routes/example.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db

router = APIRouter()

@router.get("/example")
async def get_example(db: AsyncSession = Depends(get_db)):
    return {"message": "Hello World"}
```

### Database Models

Models are defined using SQLAlchemy with async support:

```python
# app/models/example.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid

class Example(Base):
    __tablename__ = "examples"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Database Migrations

Use Alembic for database migrations:

```bash
# Create migration
alembic revision --autogenerate -m "Add example table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Middleware Development

Middleware is organized in `app/middleware/`:

```python
# app/middleware/example.py
from fastapi import Request
from fastapi.responses import JSONResponse

async def example_middleware(request: Request, call_next):
    # Pre-processing
    response = await call_next(request)
    # Post-processing
    return response
```

## Frontend Development

### Component Structure

Components are organized by feature:

```
src/components/
├── IOC/              # IOC-related components
├── Layout/           # Layout components
└── Auth/            # Authentication components
```

### Styling

Use CSS Modules for component-specific styles:

```css
/* Component.module.css */
.container {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1rem;
}

.title {
  color: var(--text-primary);
  font-size: 1.5rem;
}
```

### State Management

Use React Context for global state:

```javascript
// lib/auth.jsx
import { createContext, useContext, useState } from 'react';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  
  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
```

## Testing

### Backend Testing

Use pytest with async support:

```python
# app/tests/test_example.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_example_endpoint(client: AsyncClient):
    response = await client.get("/api/example")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello World"
```

Run tests:
```bash
pytest
```

### Frontend Testing

Use Vitest with React Testing Library:

```javascript
// src/tests/components/Example.test.jsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Example from '../../components/Example';

describe('Example', () => {
  it('renders correctly', () => {
    render(<Example />);
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });
});
```

Run tests:
```bash
npm test
```

## Security Considerations

### Input Validation

All inputs are validated using Pydantic schemas:

```python
# app/schemas/example.py
from pydantic import BaseModel, validator

class ExampleRequest(BaseModel):
    name: str
    value: int
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) > 100:
            raise ValueError('Name too long')
        return v
```

### Authentication

Use JWT tokens for authentication:

```python
# app/api/routes/auth.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Validate token and return user
    pass
```

### Rate Limiting

Rate limiting is implemented as middleware:

```python
# app/middleware/rate_limit.py
async def rate_limit_middleware(request: Request, call_next):
    # Check rate limits
    # Return 429 if exceeded
    pass
```

## Performance Optimization

### Database Optimization

- Use connection pooling
- Implement proper indexing
- Use async database operations
- Monitor query performance

### Caching

- Redis for application caching
- HTTP caching headers
- Database query caching

### Memory Management

- Monitor memory usage
- Implement garbage collection
- Use memory-efficient data structures

## Monitoring and Logging

### Health Checks

Implement health check endpoints:

```python
@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": await check_database(),
            "redis": await check_redis()
        }
    }
```

### Metrics Collection

Collect application metrics:

```python
# app/middleware/metrics.py
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Record metrics
    await record_request_metrics(request, response, duration)
    
    return response
```

### Logging

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("User action", extra={
    "user_id": user.id,
    "action": "ioc_check",
    "ioc": ioc_value
})
```

## Deployment

### Docker Deployment

Use Docker Compose for development:

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_DSN=postgresql://user:pass@db:5432/flashthreat
      - REDIS_URL=redis://redis:6379
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=flashthreat
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
  
  redis:
    image: redis:6
```

### Production Deployment

1. **Environment Configuration:**
   - Set production environment variables
   - Configure SSL certificates
   - Set up monitoring and logging

2. **Database Setup:**
   - Run migrations: `alembic upgrade head`
   - Create initial users
   - Set up backups

3. **Security Configuration:**
   - Configure CORS properly
   - Set up rate limiting
   - Enable security headers

## API Documentation

### OpenAPI/Swagger

FastAPI automatically generates OpenAPI documentation:
- Available at `/docs` endpoint
- Interactive API testing
- Schema validation

### Custom Documentation

Add detailed docstrings to endpoints:

```python
@router.post("/check_ioc", summary="Check an IOC against all providers")
async def check_ioc(
    ioc_check: IOCCheck,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Check an IOC against all providers and return the results.
    
    Args:
        ioc_check: IOC check request with IOC value and options
        db: Database session for data persistence
        
    Returns:
        Dictionary containing lookup ID, provider results, and summary
        
    Raises:
        HTTPException: If IOC format is invalid or providers are unavailable
    """
```

## Contributing

### Code Style

- **Python**: Use Black for formatting, isort for imports
- **JavaScript**: Use Prettier for formatting, ESLint for linting
- **Type Hints**: Use type hints for all Python functions
- **Documentation**: Document all public functions and classes

### Git Workflow

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and commit: `git commit -m "Add new feature"`
3. Push branch: `git push origin feature/new-feature`
4. Create pull request

### Testing Requirements

- All new code must have tests
- Maintain test coverage above 80%
- Include integration tests for new endpoints
- Test security features thoroughly

## Troubleshooting

### Common Issues

#### Database Connection Issues
- Check connection string format
- Verify database is running
- Check network connectivity

#### Redis Connection Issues
- Verify Redis is running
- Check connection URL
- Monitor Redis memory usage

#### API Rate Limiting
- Check rate limit configuration
- Monitor Redis for rate limit data
- Adjust limits if needed

#### Performance Issues
- Monitor system metrics
- Check database query performance
- Review caching strategy

### Debug Mode

Enable debug mode for development:

```python
# app/core/config.py
class Settings(BaseSettings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
```

### Logging Configuration

Configure logging for development:

```python
# logging.conf
[loggers]
keys=root,flashthreat

[handlers]
keys=console

[formatters]
keys=default

[logger_flashthreat]
level=DEBUG
handlers=console
qualname=flashthreat

[handler_console]
class=StreamHandler
level=DEBUG
formatter=default
args=(sys.stdout,)

[formatter_default]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://reactjs.org/docs/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Alembic Documentation**: https://alembic.sqlalchemy.org/
- **Redis Documentation**: https://redis.io/documentation
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
