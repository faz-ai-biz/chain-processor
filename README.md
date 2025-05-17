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

## Using Text Processing Nodes with the API

The Chain Processor Core package includes built-in text processing nodes (like `UppercaseNode`, `LowercaseNode`, etc.) that can be used to create processing chains. To use these nodes with the API, follow these steps:

### 1. Register the Nodes in the Database

The nodes are defined in the code, but must be registered in the database before they can be used in chains:

```bash
# Copy the registration script to the API container
docker cp docker_register_nodes.py chain-processor-api:/app/docker_register_nodes.py

# Run the script inside the container
docker exec -it chain-processor-api python /app/docker_register_nodes.py
```

This registers all the built-in text processing nodes in the database. You should see output confirming the registration of nodes like `UppercaseNode`, `LowercaseNode`, `count_words`, etc.

### 2. Create and Run Processing Chains

Once the nodes are registered, you can use the API to:
1. Create a chain strategy
2. Add nodes to the chain
3. Execute the chain with text input

The `docker_demo.py` script demonstrates this workflow:

```bash
python docker_demo.py
```

> **Note**: There's currently an issue with chain execution in the API where you might encounter an error: `'str' object has no attribute 'value'`. This happens in the `chains.py` file where it's trying to use `ExecutionStatus.IN_PROGRESS.value`, but `ExecutionStatus.IN_PROGRESS` is a string. If you encounter this, you can fix it by modifying `chain-processor-api/src/chain_processor_api/api/chains.py` and changing instances of `ExecutionStatus.XXX.value` to just `ExecutionStatus.XXX`.

### 3. Creating Custom Chains Manually

You can also create chains manually using the API:

```bash
# 1. List available registered nodes
curl http://localhost:8095/api/nodes/

# 2. Create a chain strategy
curl -X POST "http://localhost:8095/api/chains/" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Text Chain", "description": "Custom text processing", "tags": ["demo"]}'

# 3. Add nodes to the chain (replace UUIDs with actual values)
curl -X POST "http://localhost:8095/api/chains/{chain_id}/nodes" \
  -H "Content-Type: application/json" \
  -d '{"node_id": "{node_uuid}", "position": 1, "config": {}}'

# 4. Execute the chain
curl -X POST "http://localhost:8095/api/chains/{chain_id}/execute" \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Hello world!"}'
```

### 4. Creating Custom Nodes

To create custom text processing nodes, extend the `TextChainNode` class and implement the `process` method:

```python
from chain_processor_core.lib_chains.base import TextChainNode
from chain_processor_core.lib_chains.registry import register_node

@register_node(tags=["text", "custom"])
class MyCustomNode(TextChainNode):
    """My custom node that does something with text."""
    
    def process(self, input_text: str) -> str:
        """Process the input text."""
        self.validate_input(input_text)
        # Custom processing logic here
        return input_text.replace("hello", "goodbye")
```

## Testing

Each package contains its own test suite. To run all tests at once:

```bash
pytest
```

## License

MIT License

