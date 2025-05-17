#!/bin/bash
set -e

# Start PostgreSQL container for testing
echo "Starting PostgreSQL container for testing..."
docker compose -f docker-compose.test.yml up -d postgres_test

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
docker compose -f docker-compose.test.yml run --rm test bash -c "while ! nc -z postgres_test 5432; do sleep 1; done"

# Run tests
echo "Running tests..."
docker compose -f docker-compose.test.yml run --rm test pytest "$@"

# Cleanup
echo "Cleaning up..."
docker compose -f docker-compose.test.yml down

echo "Test run completed!"
