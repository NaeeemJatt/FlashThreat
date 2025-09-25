# FlashThreat

A powerful web application for analyzing Indicators of Compromise (IOCs) using multiple threat intelligence sources.

## Features

- **Single IOC Lookup**: Analyze IPs, domains, URLs, and file hashes against multiple threat intelligence sources
- **Real-time Streaming**: Results stream to the browser as they arrive from each provider
- **Unified Scoring**: Clear verdict and score based on weighted analysis of all sources
- **Caching**: Redis-based caching with configurable TTLs by IOC type
- **Permanent Storage**: PostgreSQL database for storing lookup history and results
- **Bulk Processing**: Upload CSV files for batch processing of multiple IOCs
- **User Management**: Basic authentication with admin and analyst roles

## Supported Providers

- **VirusTotal**: Comprehensive threat intelligence for all IOC types
- **AbuseIPDB**: IP reputation and abuse reports
- **Shodan**: Network exposure and vulnerability information
- **AlienVault OTX**: Open Threat Exchange for all IOC types

## Tech Stack

### Backend
- FastAPI (Python)
- SQLAlchemy with PostgreSQL
- Redis for caching
- Alembic for database migrations
- Async architecture with httpx

### Frontend
- React with Vite
- React Query for data fetching
- Server-Sent Events (SSE) for streaming
- CSS Modules for styling

## Getting Started

### Prerequisites

- Docker and Docker Compose
- API keys for the following services:
  - VirusTotal
  - AbuseIPDB
  - Shodan
  - AlienVault OTX

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/flashthreat.git
   cd flashthreat
   ```

2. Create a `.env` file from the example:
   ```
   cp .env.example .env
   ```

3. Add your API keys to the `.env` file:
   ```
   VT_API_KEY=your_virustotal_api_key
   ABUSEIPDB_API_KEY=your_abuseipdb_api_key
   SHODAN_API_KEY=your_shodan_api_key
   OTX_API_KEY=your_otx_api_key
   ```

4. Start the services with Docker Compose:
   ```
   docker-compose up -d
   ```

5. Seed the database with initial data:
   ```
   docker-compose exec backend python seed_data.py
   ```

6. Access the application at http://localhost

### Default Users

- Admin: admin@example.com / password123
- Analyst: analyst@example.com / password123

## Development

### Backend

To run the backend in development mode:

```
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

To run the frontend in development mode:

```
cd frontend
npm install
npm run dev
```

## Testing

### Backend Tests

```
cd backend
pytest
```

### Frontend Tests

```
cd frontend
npm test
```

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

