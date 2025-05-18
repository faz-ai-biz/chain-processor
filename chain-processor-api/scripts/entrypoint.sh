#!/bin/bash
# Entrypoint script for the Chain Processor API service
set -e

# Run database migrations
echo "Running database migrations..."
cd /app/chain-processor-db
alembic upgrade head

# Start API service
echo "Starting API service..."
cd /app/chain-processor-api
exec uvicorn chain_processor_api.main:app --host 0.0.0.0 --port 8000 