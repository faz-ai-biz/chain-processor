# Chain Processor DB

Database migrations and models for the Chain Processing System.

## Description

This repository contains the database layer for the Chain Processing System, including:

- SQLAlchemy ORM models
- Database migrations using Alembic
- Repository pattern implementation for data access
- Session management utilities

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14.x
- [Optional] PgBouncer for connection pooling

### Installation

```bash
# Clone the repository
git clone https://github.com/chain-processor-org/chain-processor-db.git
cd chain-processor-db

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Configuration

Set the following environment variables:

```bash
export DATABASE_URL=postgresql://user:password@localhost:5432/chain_processor
export DATABASE_POOL_SIZE=10
export DATABASE_MAX_OVERFLOW=20
```

Or create a `.env` file in the project root with these variables.

### Environment Variables

Copy the example environment file:

```bash
# Create a local .env file (ignored by git)
cat << EOF > .env
# Database connection
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chain_processor
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# For testing
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5433/chain_processor_test
EOF
```

These environment variables control:
- `DATABASE_URL`: Connection string for the main database
- `DATABASE_POOL_SIZE`: Number of connections to keep in the pool
- `DATABASE_MAX_OVERFLOW`: Maximum number of connections above pool size
- `TEST_DATABASE_URL`: Connection string for the test database

## Migration Management

To run database migrations:

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description of changes"
```

## Development

### Running Tests

#### Using Docker

The simplest way to run tests is using Docker, which eliminates the need to configure a PostgreSQL database locally:

```bash
# Make the script executable if it's not already
chmod +x scripts/run_tests.sh

# Run all tests
./scripts/run_tests.sh

# Run specific tests
./scripts/run_tests.sh tests/unit/test_repositories
```

This will:
1. Start a PostgreSQL container for testing
2. Run the tests against that database
3. Clean up the containers afterward

#### Running Tests Locally

If you prefer to run tests without Docker, you'll need to:

1. Start a PostgreSQL instance for testing
2. Set the `TEST_DATABASE_URL` environment variable
3. Run pytest

```bash
# Start PostgreSQL (you can also use the docker-compose.yml file)
docker-compose up -d postgres

# Set the database URL
export TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chain_processor_test

# Run tests
pytest
```

### Code Style

This project uses:
- Black for code formatting
- Ruff for linting
- MyPy for type checking

To check and fix code style:

```bash
# Format code
black src tests

# Lint code
ruff src tests

# Type check
mypy src
```

## Project Structure

```
chain-processor-db/
├── alembic/                 # Database migrations
├── src/
│   └── chain_processor_db/
│       ├── __init__.py
│       ├── session.py       # Database session management
│       ├── base.py          # Base model and metadata
│       ├── models/          # ORM models
│       └── repositories/    # Data access layer
├── docs/
│   ├── adr/                 # Architecture Decision Records
│   └── schema/              # Database schema documentation
└── tests/
    ├── unit/               # Unit tests
    └── integration/        # Integration tests
```

## Implementation Details

The Chain Processor DB component follows several key design principles:

### Repository Pattern

We use the Repository Pattern to provide a clean abstraction over data access. Each domain entity has a dedicated repository class that inherits from a generic `BaseRepository[T]` class. This approach:

- Separates data access concerns from business logic
- Promotes testability through dependency injection
- Provides consistent CRUD operations across all entities
- Allows for specialized query methods

See the [ADR on Repository Pattern](docs/adr/001_repository_pattern.md) for more details.

### SQLAlchemy ORM with Type Safety

We leverage SQLAlchemy 2.0's ORM with Python's type annotations to create a fully typed database layer:

- Models use SQLAlchemy's mapped attributes for type safety
- Repositories are implemented as generic classes for proper return types
- All parameters and return values have appropriate type hints

### Migration Management with Alembic

Database schema migrations are handled with Alembic:

- Initial migration creates the complete schema
- Subsequent migrations will be generated using Alembic's autogenerate feature
- Migrations are tracked in version control and applied consistently across environments

### Connection Pooling

The database engine is configured with connection pooling to efficiently manage database connections:

- Connection pool size is configurable through environment variables
- Includes connection recycling and pre-ping validation
- Compatible with external connection poolers like PgBouncer

## Database Schema

For a detailed description of the database schema, see the [schema documentation](docs/schema/database_schema.md).

## Development with Docker

For local development, you can use Docker Compose to start a PostgreSQL database and pgAdmin interface:

```bash
# Start the development environment
docker-compose up -d

# Access pgAdmin at http://localhost:5050
# - Email: admin@example.com
# - Password: admin
```

The PostgreSQL server will be accessible at:
- Host: localhost
- Port: 5432
- User: postgres
- Password: postgres
- Database: chain_processor 

### Using the Makefile

A Makefile is provided for common development tasks:

```bash
# Setup development environment
make setup

# Run tests
make test

# Run tests with Docker
make test-docker

# Run tests with coverage
make test-cov

# Run linting
make lint

# Format code
make format

# Run database migrations
make migrate

# Start development environment
make dev

# Stop and clean development environment
make clean

# Create a new migration (will prompt for description)
make migration
``` 
