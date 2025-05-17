# Chain Processor API

REST API service for the Chain Processing System.

## Development Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e .[dev]
uvicorn chain_processor_api.main:app --reload
```

## Running Tests

Use Docker to run tests in an isolated PostgreSQL environment:

```bash
make test-docker
```
