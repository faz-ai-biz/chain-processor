# Chain Processor Core Documentation

Welcome to the Chain Processor Core documentation. This library provides the foundation for the Chain Processing System, including domain models, interfaces, and utilities shared across all services.

## Contents

- [Overview](#overview)
- [Installation](#installation)
- [API Reference](#api-reference)
- [Architecture Decisions](#architecture-decisions)

## Overview

The Chain Processor Core is the foundation of the Chain Processing System. It defines:

- Domain models using Pydantic
- Common exception hierarchy
- Base classes for chain nodes
- Shared utility functions

## Installation

```bash
pip install chain-processor-core
```

For development:

```bash
pip install -e ".[dev]"
```

## API Reference

### Models

- [Chain](./api/models/chain.md) - Chain and strategy models
- [Node](./api/models/node.md) - Node models
- [Execution](./api/models/execution.md) - Execution tracking models
- [User](./api/models/user.md) - User and authentication models

### Exceptions

- [Errors](./api/exceptions/errors.md) - Common exception hierarchy

### Chain Libraries

- [Base](./api/lib_chains/base.md) - Base classes for chain nodes
- [Registry](./api/lib_chains/registry.md) - Node registry

### Utilities

- [Validation](./api/utils/validation.md) - Input validation utilities
- [Serialization](./api/utils/serialization.md) - Data serialization utilities

## Architecture Decisions

See the [Architecture Decision Records](./adr/index.md) for details on architectural decisions. 