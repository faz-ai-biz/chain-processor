.PHONY: setup test test-docker lint format migrate dev clean

# Setup development environment
setup:
	uv pip install -e ".[dev]"

# Run tests
test:
	pytest

# Run tests with Docker
test-docker:
	./scripts/run_tests.sh

# Run tests with coverage
test-cov:
	pytest --cov=chain_processor_db

# Run linting
lint:
	ruff src tests
	mypy src

# Format code
format:
	black src tests

# Run database migrations
migrate:
	alembic upgrade head

# Start development environment (PostgreSQL)
dev:
	docker-compose up -d

# Stop development environment and remove volumes
clean:
	docker-compose down -v

# Create a new migration
migration:
	@read -p "Enter migration description: " desc; \
	alembic revision --autogenerate -m "$$desc" 