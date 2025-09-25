# FlashThreat

A production-ready, enterprise-grade threat intelligence analysis platform that aggregates data from multiple security providers to analyze Indicators of Compromise (IOCs).

## 🚀 Features

### Core Functionality
- **Single IOC Lookup**: Analyze IPs, domains, URLs, and file hashes against multiple threat intelligence sources
- **Real-time Streaming**: Results stream to the browser as they arrive from each provider
- **Unified Scoring**: Clear verdict and score based on weighted analysis of all sources
- **Bulk Processing**: Upload CSV files for batch processing of multiple IOCs
- **History Tracking**: Complete audit trail of analyses with detailed results

### Enterprise Features
- **Advanced Security**: Rate limiting, input sanitization, XSS protection, and security headers
- **Comprehensive Monitoring**: System health checks, performance metrics, and error tracking
- **Mobile Optimized**: Responsive design with touch-friendly interface
- **Production Ready**: Connection pooling, memory optimization, and error handling
- **Comprehensive Testing**: Integration tests, security tests, and performance validation

## Supported Providers

- **VirusTotal**: Comprehensive threat intelligence for all IOC types
- **AbuseIPDB**: IP reputation and abuse reports
- **Shodan**: Network exposure and vulnerability information
- **AlienVault OTX**: Open Threat Exchange for all IOC types

## 🛠️ Tech Stack

### Backend
- **FastAPI** (Python) with async/await support
- **PostgreSQL** with SQLAlchemy ORM and connection pooling
- **Redis** for caching and distributed rate limiting
- **Alembic** for database migrations with rollback support
- **Comprehensive Middleware**: Rate limiting, security, error handling, metrics

### Frontend
- **React 18** with modern hooks and context
- **Vite** for fast development and building
- **CSS Modules** with responsive design and mobile optimization
- **Server-Sent Events (SSE)** for real-time streaming
- **Vitest** with React Testing Library for testing

### Infrastructure
- **Docker Compose** for multi-service deployment
- **Comprehensive Monitoring** with health checks and metrics
- **Security Headers** and input sanitization
- **Production-Ready** error handling and logging

## 🚀 Getting Started

### Prerequisites

- **Docker and Docker Compose**
- **API Keys** for the following services:
  - [VirusTotal](https://www.virustotal.com/gui/join-us) - Free tier available
  - [AbuseIPDB](https://www.abuseipdb.com/pricing) - Free tier available
  - [Shodan](https://account.shodan.io/register) - Free tier available
  - [AlienVault OTX](https://otx.alienvault.com/api) - Free tier available

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/flashthreat.git
   cd flashthreat
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Configure API keys in `.env`:**
   ```bash
   VT_API_KEY=your_virustotal_api_key
   ABUSEIPDB_API_KEY=your_abuseipdb_api_key
   SHODAN_API_KEY=your_shodan_api_key
   OTX_API_KEY=your_otx_api_key
   ```

4. **Start the application:**
   ```bash
   docker-compose up -d
   ```

5. **Initialize the database:**
   ```bash
   docker-compose exec backend python init_db.py
   ```

6. **Access the application:**
   - **Frontend**: http://localhost:3000
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/api/providers/health

### Default Users

- **Admin**: `admin@flashthreat.local` / `admin123`
- **Analyst**: `analyst@flashthreat.local` / `analyst123`

## 🔧 Development

### Backend Development

```bash
cd backend
pip install poetry
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
poetry run pytest
poetry run pytest --cov=app tests/  # With coverage
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage  # With coverage
```

### Integration Tests

```bash
cd backend
poetry run pytest tests/test_integration.py
poetry run pytest tests/test_security.py
```

## 📚 Documentation

- **[API Documentation](docs/API_DOCUMENTATION.md)**: Complete REST API reference
- **[User Guide](docs/USER_GUIDE.md)**: End-user documentation
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)**: Technical documentation for contributors
- **[Project Analysis](PROJECT_ANALYSIS_REMAINING.md)**: Remaining areas for improvement

## 🔒 Security Features

- **Rate Limiting**: 60 requests/minute, 1000 requests/hour per IP
- **Input Sanitization**: XSS and SQL injection protection
- **Security Headers**: CSP, HSTS, X-Frame-Options, and more
- **Authentication**: JWT-based with role-based access control
- **Error Handling**: Secure error responses without information leakage

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Redis](https://redis.io/)
- [VirusTotal](https://www.virustotal.com/)
- [AbuseIPDB](https://www.abuseipdb.com/)
- [Shodan](https://www.shodan.io/)
- [AlienVault OTX](https://otx.alienvault.com/)

