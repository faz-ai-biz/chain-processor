# Chain Processor Monorepo

This repository combines multiple packages that together make up the **Chain Processing System**. Each package lives in its own directory and can be developed separately.

## Packages

- **chain-processor-api** – FastAPI service providing the public REST API.
- **chain-processor-core** – Shared domain models, exceptions and utilities.
- **chain-processor-db** – SQLAlchemy models, repositories and database migrations.

See the `README.md` in each package for detailed setup instructions.

## Running the Stack

The easiest way to start all services for local development is via Docker Compose:

```bash
docker compose up -d
```

This command launches PostgreSQL, applies any pending database migrations and starts the API and core services. Once running, access the API documentation at:

- http://localhost:8095/docs – Swagger UI
- http://localhost:8095/redoc – ReDoc

To stop the stack:

```bash
docker compose down
```

## Testing

Each package contains its own test suite. To run all tests at once:

```bash
pytest
```

## License

MIT License

