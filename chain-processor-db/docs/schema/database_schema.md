# Chain Processor DB - Database Schema

This document describes the database schema for the Chain Processing System.
ORM models expose JSONB columns named `metadata` using the attribute
`metadata_json` to avoid conflicts with SQLAlchemy's reserved `metadata`
attribute.

## Entity Relationship Diagram

```
                   ┌──────────────┐                ┌──────────────┐
                   │     User     │                │     Node     │
                   ├──────────────┤                ├──────────────┤
                   │ id           │                │ id           │
                   │ email        │                │ name         │
                   │ password_hash│                │ description  │
                   │ full_name    │◄───────────────┤ code         │
                   │ is_active    │                │ created_by_id│
                   │ is_superuser │                │ is_builtin   │
                   │ roles        │                │ is_active    │
                   │ preferences  │                │ metadata     │
                   │ last_login   │                │ tags         │
                   └──────┬───────┘                └──────┬───────┘
                          │                                │
                          │                                │
                   ┌──────▼───────┐                ┌───────▼──────┐
                   │ChainStrategy │◄───────────────┤ StrategyNode │
                   ├──────────────┤                ├──────────────┤
                   │ id           │                │ id           │
                   │ name         │                │ strategy_id  │
                   │ description  │                │ node_id      │
                   │ created_by_id│                │ position     │
                   │ is_active    │                │ config       │
                   │ tags         │                │              │
                   │ metadata     │                │              │
                   └──────┬───────┘                └──────────────┘
                          │
                          │
                   ┌──────▼───────┐
                   │ChainExecution│
                   ├──────────────┤
                   │ id           │
                   │ strategy_id  │
                   │ input_text   │
                   │ output_text  │
                   │ error        │
                   │ status       │
                   │ started_at   │
                   │ completed_at │
                   │ exec_time_ms │
                   │ created_by_id│
                   │ metadata     │
                   └──────┬───────┘
                          │
                          │
                   ┌──────▼───────┐
                   │NodeExecution │
                   ├──────────────┤
                   │ id           │
                   │ execution_id │
                   │ node_id      │
                   │ input_text   │
                   │ output_text  │
                   │ error        │
                   │ status       │
                   │ started_at   │
                   │ completed_at │
                   │ exec_time_ms │
                   │ metadata     │
                   └──────────────┘
```

## Tables

### User

Stores user information for authentication and authorization.

| Column        | Type            | Description                      |
|---------------|-----------------|----------------------------------|
| id            | UUID            | Primary key                      |
| email         | String(255)     | User email (unique)              |
| password_hash | String(255)     | Hashed password                  |
| full_name     | String(255)     | User's full name                 |
| is_active     | Boolean         | Whether the user is active       |
| is_superuser  | Boolean         | Whether the user is a superuser  |
| roles         | Array[String]   | List of user roles               |
| preferences   | JSONB           | User preferences                 |
| last_login    | DateTime        | Last login timestamp             |
| created_at    | DateTime        | Creation timestamp               |
| updated_at    | DateTime        | Last update timestamp            |
| version       | Integer         | Version number                   |

### Node

Stores processing nodes that can be used in chains.

| Column        | Type            | Description                     |
|---------------|-----------------|---------------------------------|
| id            | UUID            | Primary key                     |
| name          | String(255)     | Node name                       |
| description   | Text            | Node description                |
| code          | Text            | Node code                       |
| created_by_id | UUID            | ID of the creator (User)        |
| is_builtin    | Boolean         | Whether the node is built-in    |
| is_active     | Boolean         | Whether the node is active      |
| metadata      | JSONB           | Node metadata                   |
| tags          | Array[String]   | List of tags                    |
| created_at    | DateTime        | Creation timestamp              |
| updated_at    | DateTime        | Last update timestamp           |
| version       | Integer         | Version number                  |

### ChainStrategy

Stores chain strategies that define how nodes are connected.

| Column        | Type            | Description                      |
|---------------|-----------------|----------------------------------|
| id            | UUID            | Primary key                      |
| name          | String(255)     | Strategy name                    |
| description   | Text            | Strategy description             |
| created_by_id | UUID            | ID of the creator (User)         |
| is_active     | Boolean         | Whether the strategy is active   |
| tags          | Array[String]   | List of tags                     |
| metadata      | JSONB           | Strategy metadata                |
| created_at    | DateTime        | Creation timestamp               |
| updated_at    | DateTime        | Last update timestamp            |
| version       | Integer         | Version number                   |

### StrategyNode

Joins chain strategies and nodes with position information.

| Column        | Type            | Description                      |
|---------------|-----------------|----------------------------------|
| id            | UUID            | Primary key                      |
| strategy_id   | UUID            | ID of the strategy               |
| node_id       | UUID            | ID of the node                   |
| position      | Integer         | Position in the chain            |
| config        | JSONB           | Node-specific configuration      |
| created_at    | DateTime        | Creation timestamp               |
| updated_at    | DateTime        | Last update timestamp            |

### ChainExecution

Stores execution records for chains.

| Column        | Type            | Description                      |
|---------------|-----------------|----------------------------------|
| id            | UUID            | Primary key                      |
| strategy_id   | UUID            | ID of the strategy               |
| input_text    | Text            | Input text                       |
| output_text   | Text            | Output text                      |
| error         | Text            | Error message                    |
| status        | String(20)      | Execution status                 |
| started_at    | DateTime        | Start timestamp                  |
| completed_at  | DateTime        | Completion timestamp             |
| execution_time_ms | Integer     | Execution time in milliseconds   |
| created_by_id | UUID            | ID of the creator (User)         |
| metadata      | JSONB           | Execution metadata               |
| created_at    | DateTime        | Creation timestamp               |
| updated_at    | DateTime        | Last update timestamp            |
| version       | Integer         | Version number                   |

### NodeExecution

Stores execution records for individual nodes.

| Column        | Type            | Description                      |
|---------------|-----------------|----------------------------------|
| id            | UUID            | Primary key                      |
| execution_id  | UUID            | ID of the chain execution        |
| node_id       | UUID            | ID of the node                   |
| input_text    | Text            | Input text                       |
| output_text   | Text            | Output text                      |
| error         | Text            | Error message                    |
| status        | String(20)      | Execution status                 |
| started_at    | DateTime        | Start timestamp                  |
| completed_at  | DateTime        | Completion timestamp             |
| execution_time_ms | Integer     | Execution time in milliseconds   |
| metadata      | JSONB           | Execution metadata               |
| created_at    | DateTime        | Creation timestamp               |
| updated_at    | DateTime        | Last update timestamp            |

## Indexes

The following indexes are created to optimize query performance:

- `ix_users_email` - Unique index on users.email
- `ix_nodes_name` - Index on nodes.name
- `ix_chain_strategies_name` - Index on chain_strategies.name
- `ix_strategy_nodes_strategy_id` - Index on strategy_nodes.strategy_id
- `ix_strategy_nodes_node_id` - Index on strategy_nodes.node_id
- `ix_chain_executions_strategy_id` - Index on chain_executions.strategy_id
- `ix_chain_executions_status` - Index on chain_executions.status
- `ix_node_executions_execution_id` - Index on node_executions.execution_id
- `ix_node_executions_node_id` - Index on node_executions.node_id
- `ix_node_executions_status` - Index on node_executions.status 