# Chain Processor API

A microservice API for executing and managing text processing chains.

## Overview

The Chain Processor API provides endpoints for:

1. Creating and managing chain strategies (sequences of processing nodes)
2. Viewing available node types
3. Executing chains with text input 
4. Reviewing execution history and results

## Key Endpoints

### Chain Management

- `GET /api/chains`: List all available chain strategies
- `POST /api/chains`: Create a new chain strategy
- `POST /api/chains/{chain_id}/execute`: Execute a chain with input text

### Node Management

- `GET /api/nodes`: List all registered nodes in the database
- `GET /api/nodes/available`: List all available node types in the registry
- `GET /api/nodes/tags`: List all available node tags

### Execution History

- `GET /api/executions`: List all chain executions
- `GET /api/executions/{execution_id}`: Get details of a specific execution

## Example Usage

### Creating a Chain

```bash
curl -X POST "http://localhost:8000/api/chains/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Text Transformer", "description": "Converts text to uppercase and then counts words", "tags": ["demo", "text"]}'
```

### Adding Nodes to a Chain

After creating a chain, use the ID to add nodes to it:

```bash
curl -X POST "http://localhost:8000/api/chains/{chain_id}/nodes" \
  -H "Content-Type: application/json" \
  -d '{"node_id": "{node_id}", "position": 0, "config": {}}'
```

### Executing a Chain

```bash
curl -X POST "http://localhost:8000/api/chains/{chain_id}/execute" \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Hello world! This is a test."}'
```

## Development

### Setup

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Run the development server:
   ```bash
   uvicorn chain_processor_api.main:app --reload
   ```

3. Access the API documentation:
   ```
   http://localhost:8000/docs
   ```

### Running Tests

```bash
pytest
```

## Architecture

The Chain Processor system is composed of three main components:

1. **chain-processor-api**: FastAPI-based web service exposing REST endpoints
2. **chain-processor-core**: Core library with chain processing logic and node registry
3. **chain-processor-db**: Database models and repositories for persistence

## Available Node Types

The system comes with several built-in node types:

- `UppercaseNode`: Converts text to uppercase
- `LowercaseNode`: Converts text to lowercase
- `ReverseTextNode`: Reverses the input text
- `remove_whitespace`: Removes all whitespace from text
- `count_words`: Counts words in the input text
- `count_characters`: Counts characters in the input text

Custom nodes can be added by extending the core library.

## Postman Collection

The repository includes a Postman collection located at `../docs/postman_collection.json`. Import this file into Postman to exercise all API endpoints. The collection uses a `base_url` variable that defaults to `http://localhost:8000`. Adjust this variable to match your running server URL.
