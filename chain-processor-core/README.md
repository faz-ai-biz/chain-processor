# Chain Processor Core

Core processing library for the Chain Processing System. This package contains node definitions, chain execution logic, and a registry system for managing nodes.

## Overview

Chain Processor Core provides:

1. Abstract base classes for processing nodes
2. A registry for looking up nodes by name
3. Chain execution functionality
4. Built-in node implementations for common text processing tasks

## Node Types

The system is designed around the concept of chain nodes, which are processing units that transform input data (primarily text) and can be chained together to form processing pipelines.

### Base Classes

- `ChainNode[T, U]`: Generic abstract base class for all nodes
- `TextChainNode`: Specialization for nodes that process text (input and output are strings)
- `FunctionNode`: A node that wraps a simple Python function

## Creating Custom Nodes

There are two ways to create custom nodes:

### 1. Using Class Inheritance

Create a class that inherits from `TextChainNode` and implements the `process` method:

```python
from chain_processor_core.lib_chains.base import TextChainNode
from chain_processor_core.lib_chains.registry import register_node

@register_node(tags=["text", "custom"])
class MyCustomNode(TextChainNode):
    """My custom node that does something with text."""
    
    def process(self, input_text: str) -> str:
        """Process the input text."""
        self.validate_input(input_text)
        # Do something with the text
        return input_text.replace("hello", "goodbye")
```

### 2. Using Function Decorators

Create a simple function and decorate it to convert it into a node:

```python
from chain_processor_core.lib_chains.registry import register_function_node

@register_function_node(tags=["text", "custom"])
def my_custom_processor(input_text: str) -> str:
    """Convert text to a different format."""
    return "-".join(input_text.split())
```

## Using the Registry

Nodes are registered with the global `default_registry`, which can be used to look up nodes by name:

```python
from chain_processor_core.lib_chains.registry import default_registry

# List all registered nodes
all_nodes = default_registry.list_nodes()

# Get nodes by tag
text_nodes = default_registry.list_nodes(tag="text")

# Get a node instance
node = default_registry.get_node_instance("MyCustomNode")
```

## Chain Execution

To execute a chain of nodes:

```python
from chain_processor_core.executor.chain_executor import ChainExecutor

# Define a chain as a list of (node_name, config) tuples
node_configs = [
    ("UppercaseNode", {}),
    ("count_words", {})
]

# Create an executor
executor = ChainExecutor()

# Execute the chain
result = executor.execute_chain(
    chain_id="my-chain",
    input_data="Hello world! This is a test.",
    node_configs=node_configs
)

# Access the result
print(f"Final output: {result.output_data}")
print(f"Execution time: {result.execution_time_ms}ms")

# Access individual node results
for node_result in result.node_results:
    print(f"Node {node_result.node_id}: {node_result.output_data}")
```

## Built-in Nodes

The library comes with several built-in nodes:

- `UppercaseNode`: Converts text to uppercase
- `LowercaseNode`: Converts text to lowercase
- `ReverseTextNode`: Reverses the input text
- `remove_whitespace`: Removes all whitespace from text
- `count_words`: Counts words in the input text
- `count_characters`: Counts characters in the input text

## Development

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Testing

```bash
pytest
```

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

2. Set up a virtual environment (requires Python 3.11+):

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
