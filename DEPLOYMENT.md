# Chain Processor Deployment

This document provides instructions for deploying the Chain Processor system using Docker Compose.

## Prerequisites

- Docker and Docker Compose installed on your system
- Git repository cloned locally

## Components

The Chain Processor system consists of the following components:

1. **chain-processor-db**: PostgreSQL database service
2. **chain-processor-api**: FastAPI application providing REST endpoints
3. **chain-processor-core**: Core processing logic
4. **pgadmin**: Optional web UI for database management

## Deployment Steps

1. Navigate to the root directory of the repository:

```bash
cd /path/to/core-chain-nlp
```

2. Build and start all services:

```bash
docker compose up -d
```

3. To check the status of the services:

```bash
docker compose ps
```

4. Access the API documentation at:
   - http://localhost:8000/api/docs (Swagger UI)
   - http://localhost:8000/api/redoc (ReDoc)

5. Access PGAdmin (database management) at:
   - http://localhost:5050
   - Login with:
     - Email: admin@example.com
     - Password: admin

6. To stop all services:

```bash
docker compose down
```

7. To stop and remove all data volumes:

```bash
docker compose down -v
```

## Environment Configuration

You can customize the deployment by creating a `.env` file in the root directory with the following variables:

```
# Database settings
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=chain_processor

# API settings
CORS_ORIGINS=["*"]
```

## Health Check

The API provides a health check endpoint at:
- http://localhost:8000/health 