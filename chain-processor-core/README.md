# Chain Processor Core

Central shared library containing domain models, interfaces, and utilities used across all services in the Chain Processing System.

## Overview

The Chain Processor Core provides the foundation for the entire Chain Processing System. It defines the domain models, shared interfaces, and utility functions that ensure consistency across different services.

## Features

- Domain models using Pydantic for validation and serialization
- Common exception hierarchy for consistent error handling
- Base classes for chain nodes with standardized interfaces
- Utility functions for shared operations

## Installation

```bash
pip install chain-processor-core
```

For development:

```bash
pip install -e ".[dev]"
```

## Development Setup

1. Clone the repository:

```bash
git clone https://github.com/chain-processor-org/chain-processor-core.git
cd chain-processor-core
```

2. Set up a virtual environment (requires Python 3.13+):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -e ".[dev]"
```

4. Run tests:

```bash
pytest
```

## Project Structure

```
chain-processor-core/
├── src/
│   └── chain_processor_core/
│       ├── models/          # Pydantic models
│       ├── exceptions/      # Common exceptions
│       ├── lib_chains/      # Base classes for chain nodes
│       └── utils/           # Shared utilities
├── docs/
│   ├── adr/                 # Architecture Decision Records
│   └── index.md             # Documentation index
└── tests/
    └── unit/               # Unit tests
```

## Usage

```python
from chain_processor_core.models.chain import Chain, ChainStrategyCreate
from chain_processor_core.models.node import Node, NodeReference
from chain_processor_core.exceptions.errors import ChainProcessorError
from chain_processor_core.lib_chains.base import ChainNode

# Create some nodes
node1 = Node(name="First Node", code="print('first')")
node2 = Node(name="Second Node", code="print('second')")

# Define the node order for the strategy
strategy = ChainStrategyCreate(
    name="Example Chain",
    nodes=[
        NodeReference(node_id=node1.id, position=1),
        NodeReference(node_id=node2.id, position=2),
    ],
)

# Combine strategy and nodes into a chain
chain = Chain(strategy=strategy, nodes=[node1, node2])

# Exception handling
try:
    # Your code here
    pass
except ChainProcessorError as e:
    print(f"Chain processor error: {e}")
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

MIT License 