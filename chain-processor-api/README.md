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

## Postman Collection

The repository includes a Postman collection located at `../docs/postman_collection.json`. Import this file into Postman to exercise all API endpoints. The collection uses a `base_url` variable that defaults to `http://localhost:8000`. Adjust this variable to match your running server URL.
