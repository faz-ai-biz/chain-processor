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

### Running the Demo

A comprehensive demo script is included to showcase the complete workflow:

```bash
python demo_chain_processor.py
```

This script demonstrates:
1. Checking for nodes in the database
2. Creating a chain strategy
3. Adding nodes to the chain
4. Executing the chain with sample text
5. Displaying the results

### Manual Steps

If you prefer to understand the process step-by-step:

#### 1. Register the Nodes in the Database

The nodes are defined in the code, but must be registered in the database before they can be used in chains. You'll need to create a script similar to this:

```python
from chain_processor_core.lib_chains.registry import default_registry
from chain_processor_core.lib_chains.base import TextChainNode
from chain_processor_core.nodes import text_processing  # Make sure this is imported

from chain_processor_db.session import get_db
from chain_processor_db.models.node import Node
from chain_processor_db.repositories.node_repo import NodeRepository

# Get available nodes from registry
nodes = default_registry.list_nodes()
print(f"Found {len(nodes)} nodes in registry")

# Register them in database
db = next(get_db())
node_repo = NodeRepository(db)

for name in nodes:
    # Get node details, create DB entry, etc.
    # ...
```

Then run it in the Docker container:
```bash
docker cp your_script.py chain-processor-api:/app/
docker exec chain-processor-api python /app/your_script.py
```

#### 2. Creating and Running Chains

Once nodes are registered, use the API to:
1. Create a chain strategy
2. Add nodes to the chain
3. Execute the chain with text input

```bash
# Create a chain strategy
curl -X POST "http://localhost:8095/api/chains/" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Text Chain", "description": "Custom text processing", "tags": ["demo"]}'

# Add nodes to the chain (replace UUIDs with actual values)
curl -X POST "http://localhost:8095/api/chains/{chain_id}/nodes" \
  -H "Content-Type: application/json" \
  -d '{"node_id": "{node_uuid}", "position": 1, "config": {}}'

# Execute the chain
curl -X POST "http://localhost:8095/api/chains/{chain_id}/execute" \
  -H "Content-Type: application/json" \
  -d '{"input_text": "Hello world!"}'
```

### Creating Custom Nodes

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

