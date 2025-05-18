# Chain Processing System - Multi-Repository Architecture

**Specification Document – Version 1.2 (May 17, 2025)**

## 1. Introduction

The Chain Processing System is a modular platform that executes data through customizable processing nodes. This document supersedes v1.1, adding preconditions, security, observability, disaster recovery, and testing mandates. The architecture follows SOLID and DRY principles with a multi-repository approach.

## 2. Scope

This document defines functional and non-functional requirements, preconditions, and governance for all repositories. Implementation details are covered only where needed for compliance and integration.

## 3. Definitions

- **Chain**: A sequence of processing nodes that data passes through in a defined order.
- **Node**: An individual processing unit within a chain that performs a specific operation on the input data.
- **Execution Graph**: A runtime instance of a Chain with concrete inputs, outputs, and execution metrics.
- **Strategy**: A configuration that defines the order and selection of nodes within a chain.

## 4. Preconditions & Environment

| Area | Requirement |
|------|-------------|
| OS (containers) | Debian 12 / Alpine 3.20 |
| Python | ≥ 3.11 |
| Node.js | ≥ 20.11 LTS |
| PostgreSQL | 14.x |
| Docker | ≥ 24.0, BuildKit enabled |
| Kubernetes | ≥ 1.28 |
| Helm | ≥ 3.15 |
| Hardware (dev) | 8 vCPU, 16 GiB RAM minimum |
| Hardware (prod) | 16 vCPU, 32 GiB RAM minimum |

## 5. Repository Structure

```txt
Organization: chain-processor-org
│
├── chain-processor-core         # Core libraries and shared code
├── chain-processor-api          # API service
├── chain-processor-executor     # Chain execution service
├── chain-processor-web          # Web UI
├── chain-processor-db           # Database migrations and models
└── chain-processor-deployment   # Infrastructure as code
```

### 5.1 chain-processor-core

Central shared library containing domain models, interfaces, and utilities used across all services.

```txt
chain-processor-core/
├── pyproject.toml
├── README.md
├── COMPAT.md                # Cross-repo compatibility matrix
├── src/
│   └── chain_processor_core/
│       ├── __init__.py
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

### 5.2 chain-processor-db

Database schema definitions, migrations, and data access layer.

```txt
chain-processor-db/
├── pyproject.toml
├── README.md
├── alembic/                 # Database migrations
├── src/
│   └── chain_processor_db/
│       ├── __init__.py
│       ├── session.py       # Database session management
│       ├── base.py          # Base model and metadata
│       ├── models/          # ORM models
│       └── repositories/    # Data access layer
├── docs/
│   ├── adr/                 # Architecture Decision Records
│   └── schema/              # Database schema documentation
└── tests/
    ├── unit/               # Unit tests
    └── integration/        # Integration tests
```

### 5.3 chain-processor-executor

Execution service for processing chains.

```
chain-processor-executor/
├── pyproject.toml
├── README.md
├── Dockerfile
├── src/
│   └── chain_processor_executor/
│       ├── __init__.py
│       ├── main.py          # Service entry point
│       ├── config.py        # Configuration
│       ├── executor/        # Chain execution logic
│       ├── lib_chains_generated/  # Generated node code
│       └── services/        # Business services
├── docs/
│   ├── adr/                 # Architecture Decision Records
│   └── api/                 # API documentation
└── tests/
    ├── unit/               # Unit tests
    ├── integration/        # Integration tests
    └── contract/           # Contract tests
```

### 5.4 chain-processor-api

REST API service for client interactions.

```
chain-processor-api/
├── pyproject.toml
├── README.md
├── Dockerfile
├── src/
│   └── chain_processor_api/
│       ├── __init__.py
│       ├── main.py          # FastAPI application
│       ├── core/            # Core components
│       ├── api/             # API endpoints
│       └── services/        # Business services
├── docs/
│   ├── adr/                 # Architecture Decision Records
│   └── api/                 # API documentation
└── tests/
    ├── unit/               # Unit tests
    ├── integration/        # Integration tests
    └── contract/           # Contract tests
```

### 5.5 chain-processor-web

Web UI for designing and monitoring chains.

```txt
chain-processor-web/
├── package.json
├── README.md
├── Dockerfile
├── public/                  # Static assets
├── src/
│   ├── components/          # UI components
│   ├── pages/               # Application pages
│   ├── services/            # API clients
│   └── utils/               # Utilities
├── docs/
│   ├── adr/                 # Architecture Decision Records
│   └── components/          # Component documentation
├── cypress/                 # E2E tests
└── tests/
    └── unit/               # Unit tests
```

### 5.6 chain-processor-deployment

Infrastructure as code for deployment.

```txt
chain-processor-deployment/
├── README.md
├── docker-compose.yml       # Development setup
├── docker-compose.prod.yml  # Production Docker setup
├── kubernetes/              # Kubernetes manifests
├── helm/                    # Helm charts
├── observability/           # Observability configuration
│   ├── grafana/             # Grafana dashboards
│   ├── prometheus/          # Prometheus configuration
│   └── jaeger/              # Jaeger configuration
└── scripts/                 # Deployment scripts
```

## 6. Functional Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-1 | Chain Management | Create, read, update, delete, and version chains |
| FR-2 | Node Management | Create, read, update, delete, and version nodes |
| FR-3 | Chain Execution | Execute chains with tracking and metrics |
| FR-4 | User Management | Authentication, authorization, and RBAC |
| FR-5 | Versioning | Support semantic versioning for chains and nodes |
| FR-6 | Rollback | Support rolling back to previous versions |
| FR-7 | A/B Execution | Support parallel execution of different chain versions |
| FR-8 | Visual Designer | Canvas-based flow designer for chain creation |
| FR-9 | Execution Monitoring | Real-time monitoring of chain execution |
| FR-10 | Audit Logging | Capture all mutating actions for audit purposes |

## 7. Non-Functional Requirements

### 7.1 Performance

| Scenario | Load | p95 Latency | Max Latency |
|----------|------|-------------|-------------|
| Execute chain ≤ 10 nodes | 20 rps | 3s | 5s |
| Execute chain 11-30 nodes | 10 rps | 7s | 10s |
| Chain design operations | 5 rps | 1s | 3s |

### 7.2 Scalability

- Support 100+ concurrent users without performance degradation
- Horizontally scalable components (API, Executor)
- Vertical scaling for database (up to 1TB data)

### 7.3 Availability

- System availability ≥ 99.9% (excluding planned maintenance)
- Graceful degradation during partial outages
- API and Web UI must remain functional even if Executor service is unavailable

### 7.4 Accessibility

- Web UI must comply with WCAG 2.2 AA standards
- Support keyboard navigation
- Adequate color contrast for all UI elements
- Screen reader compatibility

### 7.5 Internationalization

- UI supports language packs via i18n
- Initial support for English, with extensibility for additional languages
- Date/time formats follow locale standards

## 8. Security

### 8.1 Authentication & Authorization

- JWT-based authentication
- OAuth2 support for authorization
- Role-based access control (RBAC) with predefined roles:
  - Admin: Full access to all resources
  - Editor: Create and modify chains and nodes
  - Viewer: Read-only access to chains and executions

### 8.2 Secrets Management

- Kubernetes Secrets sealed by `kubeseal`
- SOPS encryption for secrets in Git repositories
- HashiCorp Vault integration for production environments

### 8.3 Security Scanning

- Container image scanning with Trivy
- Dependency vulnerability scanning in CI pipeline
- Block deployment of images with critical vulnerabilities

### 8.4 Data Protection

- TLS 1.3 for all network communications
- At-rest encryption using AES-256
- RBAC enforcement at API and database levels
- Input validation and sanitization
- Protection against OWASP Top 10 vulnerabilities

## 9. Observability

### 9.1 Logging

- Structured JSON logs
- Centralized logging with Loki
- Log levels: ERROR, WARN, INFO, DEBUG
- Correlation IDs across service boundaries
- Proper log labeling for Loki's label-based querying

### 9.2 Metrics

- Prometheus metrics exposed via `/metrics` endpoint
- Standard metrics:
  - Request count, latency, error rate
  - Resource utilization (CPU, memory)
  - Connection pool metrics
- Custom metrics:
  - Chain execution time
  - Node execution time
  - Execution failure rate
- PgBouncer included in deployment for connection pooling with associated metrics

### 9.3 Tracing

- OpenTelemetry integration
- Distributed tracing across services
- Jaeger for trace visualization
- Automatic instrumentation for Python and JavaScript

### 9.4 Alerting

- Prometheus Alert Manager
- SLO-based alerts:
  - High latency (p95 > threshold)
  - Error rate > 1%
  - Resource saturation
- PagerDuty integration for on-call notification

### 9.5 Dashboards

- Grafana dashboards for:
  - System health
  - Chain execution metrics
  - Resource utilization
  - Error rates and latency
- Pre-configured Grafana dashboards in the deployment repository
- Loki-specific dashboards for log analysis
- Promtail configuration for proper log collection and labeling

## 10. Disaster Recovery

### 10.1 Database Backup

- PostgreSQL WAL-G continuous archiving
- Delta backups every 5 minutes
- Daily full backups
- Backup verification and restore testing
- Recovery Point Objective (RPO) ≤ 5 minutes
- Recovery Time Objective (RTO) ≤ 30 minutes

### 10.2 Code and Configuration

- Git repositories with protected branches
- Node code stored in both PostgreSQL (primary) and versioned object storage (backup)
- Daily snapshots of critical configuration
- Infrastructure as Code for rapid recovery

### 10.3 DR Testing

- Quarterly disaster recovery drills
- Documented recovery procedures
- Automated recovery scripts

## 11. Testing & CI/CD

### 11.1 Testing Requirements

- Unit tests: ≥ 90% code coverage
- Integration tests: Critical paths covered
- Contract tests: Service boundaries verified
- End-to-end tests: Key user journeys covered
- Performance tests: SLOs verified

### 11.2 CI Pipeline

```txt
.github/workflows/ci.yml:
1. Lint & type-check (ruff, mypy, eslint, tsc)
2. Accessibility checks (axe-core, pa11y)
3. Unit tests with coverage (≥ 90%)
4. Contract tests (Pact) between API and Executor
5. Build, scan, and push container images
6. Deploy to staging environment
7. Run end-to-end tests (Cypress with accessibility validation)
```

### 11.3 CD Pipeline

- GitOps approach using Argo CD
- Semantic versioning for all components
- Automated changelog generation
- Blue/green deployments
- Canary releases for critical components

## 12. Versioning & Release Management

### 12.1 Semantic Versioning

- All repositories follow SemVer (MAJOR.MINOR.PATCH)
- Breaking changes increment MAJOR version
- New features increment MINOR version
- Bug fixes increment PATCH version

### 12.2 Cross-Repository Compatibility

- Compatibility matrix maintained in `chain-processor-core/COMPAT.md`
- Core library versions anchor the matrix
- Integration tests verify compatibility across versions

### 12.3 Release Process

- Release branches created from main/master
- Release candidates tested in staging
- Automated release notes generated from commits
- Tagged releases in GitHub
- Container images tagged with version

## 13. Documentation Standards

### 13.1 Repository Documentation

- README.md with:
  - Project description
  - Setup instructions
  - Development workflow
  - Testing guidelines
- API documentation (OpenAPI/Swagger)
- Component and class documentation

### 13.2 Architecture Decision Records (ADRs)

- Each repository contains an `adr/` folder
- New architectural decisions documented as ADRs
- ADR template in `chain-processor-core/docs/adr/template.md`

### 13.3 User Documentation

- User guides for different roles
- Administrator guides
- Developer guides for extending the platform

## 14. Implementation Details

### 14.1 API Implementation

```python
# src/chain_processor_api/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .api.router import api_router
from .core.config import settings
from chain_processor_core.exceptions.errors import ChainProcessorError

app = FastAPI(
    title="Chain Processor API",
    description="API for the Chain Processor system",
    version="1.2.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Global exception handler for Chain Processor errors
@app.exception_handler(ChainProcessorError)
async def chain_processor_exception_handler(request: Request, exc: ChainProcessorError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 14.2 Chain Executor Implementation

```python
# src/chain_processor_executor/executor/chain_executor.py
import time
import uuid
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from chain_processor_core.exceptions.errors import StrategyLoadError, NodeLoadError, InvalidInputError
from chain_processor_db.models.execution import ChainExecution, NodeExecution
from chain_processor_db.repositories.chain_repo import ChainRepository
from chain_processor_db.repositories.node_repo import NodeRepository
from .node_loader import NodeLoader

class ChainExecutor:
    def __init__(self, db: Session):
        self.db = db
        self.chain_repo = ChainRepository(db)
        self.node_repo = NodeRepository(db)
        self.node_loader = NodeLoader(db)
        self.logger = logging.getLogger("chain_executor")

    async def execute_chain(self, execution_id: uuid.UUID) -> None:
        """Execute a chain based on the execution record ID."""
        # Get execution record
        execution = self.db.query(ChainExecution).filter(ChainExecution.id == execution_id).first()
        if not execution:
            raise ValueError(f"Execution not found: {execution_id}")

        # Get strategy
        strategy = self.chain_repo.get_by_id(execution.strategy_id)
        if not strategy:
            execution.status = "failed"
            execution.error = f"Strategy not found: {execution.strategy_id}"
            self.db.commit()
            return

        # Get ordered nodes with their positions
        strategy_nodes = sorted(
            strategy.strategy_nodes,
            key=lambda sn: sn.position
        )

        # Execute chain
        current_text = execution.input_text
        try:
            for strategy_node in strategy_nodes:
                node = self.node_repo.get_by_id(strategy_node.node_id)
                if not node:
                    execution.status = "failed"
                    execution.error = f"Node not found: {strategy_node.node_id}"
                    self.db.commit()
                    return

                # Create node execution record
                node_execution = NodeExecution(
                    execution_id=execution.id,
                    node_id=node.id,
                    input_text=current_text,
                    status="in_progress",
                )
                self.db.add(node_execution)
                self.db.commit()

                # Execute node
                start_time = time.time()
                try:
                    # Load and execute node
                    node_func = self.node_loader.load_node(node)
                    
                    # Check preconditions
                    if not isinstance(current_text, str):
                        raise InvalidInputError(f"Input to node {node.name} is not a string")
                    if not current_text:
                        raise InvalidInputError(f"Input to node {node.name} is empty")
                    
                    # Execute node
                    current_text = node_func(current_text)
                    
                    # Update node execution
                    node_execution.status = "success"
                    node_execution.output_text = current_text
                    node_execution.completed_at = datetime.utcnow()
                    node_execution.execution_time_ms = int((time.time() - start_time) * 1000)
                except Exception as e:
                    # Handle node execution error with proper sanitization
                    self.logger.exception(f"Error executing node {node.name}")
                    
                    # Sanitize error message to avoid leaking sensitive information
                    error_type = type(e).__name__
                    error_message = str(e)
                    sanitized_error = f"{error_type}: {self._sanitize_error_message(error_message)}"
                    
                    node_execution.status = "failed"
                    node_execution.error = sanitized_error
                    node_execution.completed_at = datetime.utcnow()
                    node_execution.execution_time_ms = int((time.time() - start_time) * 1000)
                    
                    # Update chain execution
                    execution.status = "failed"
                    execution.error = f"Error in node {node.name}: {sanitized_error}"
                    execution.completed_at = datetime.utcnow()
                    self.db.commit()
                    return
                
                self.db.commit()

            # Update chain execution
            execution.status = "success"
            execution.output_text = current_text
            execution.completed_at = datetime.utcnow()
            self.db.commit()
            
        except Exception as e:
            # Handle unexpected errors with proper sanitization
            self.logger.exception("Error executing chain")
            
            # Sanitize error message
            error_type = type(e).__name__
            error_message = str(e)
            sanitized_error = f"{error_type}: {self._sanitize_error_message(error_message)}"
            
            execution.status = "failed"
            execution.error = sanitized_error
            execution.completed_at = datetime.utcnow()
            self.db.commit()
    
    def _sanitize_error_message(self, message: str) -> str:
        """
        Sanitize error messages to prevent leaking sensitive information.
        
        Args:
            message: The raw error message
            
        Returns:
            Sanitized error message safe for storage and display
        """
        # Remove potential file paths
        import re
        message = re.sub(r'(?:/[\w/.-]+)+', '[PATH]', message)
        
        # Remove potential IPs and hostnames
        message = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP]', message)
        message = re.sub(r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b', '[HOST]', message)
        
        # Remove potential credentials
        message = re.sub(r'password\s*=\s*[\'"][^\'"]*[\'"]', 'password=[REDACTED]', message)
        message = re.sub(r'username\s*=\s*[\'"][^\'"]*[\'"]', 'username=[REDACTED]', message)
        message = re.sub(r'secret\s*=\s*[\'"][^\'"]*[\'"]', 'secret=[REDACTED]', message)
        message = re.sub(r'token\s*=\s*[\'"][^\'"]*[\'"]', 'token=[REDACTED]', message)
        
        return message
```

### 14.3 Chain Designer Implementation (Web UI)

```javascript
// src/components/Canvas/ChainDesigner.js
import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, TextField, Box, Typography, Alert } from '@mui/material';
import NodePalette from './NodePalette';
import NodeConfigPanel from './NodeConfigPanel';
import { chainService, nodeService } from '../../services';
import { topologicalSort } from '../../utils/flowUtils';

function ChainDesigner() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [strategyName, setStrategyName] = useState('');
  const [strategyDescription, setStrategyDescription] = useState('');
  const [selectedNode, setSelectedNode] = useState(null);
  const [availableNodes, setAvailableNodes] = useState([]);
  const [error, setError] = useState(null);
  const { id } = useParams();
  const navigate = useNavigate();

  // Load available nodes
  useEffect(() => {
    const fetchNodes = async () => {
      try {
        const nodes = await nodeService.getAllNodes();
        setAvailableNodes(nodes);
      } catch (err) {
        setError('Failed to load nodes');
        console.error(err);
      }
    };

    fetchNodes();
  }, []);

  // Load existing strategy if editing
  useEffect(() => {
    if (id) {
      const fetchStrategy = async () => {
        try {
          const strategy = await chainService.getStrategyById(id);
          setStrategyName(strategy.name);
          setStrategyDescription(strategy.description);
          
          // Convert strategy to flow nodes and edges
          const flowNodes = strategy.nodes.map((node, index) => ({
            id: node.id,
            type: 'customNode',
            position: { x: 250, y: 100 + index * 100 },
            data: { label: node.name, nodeData: node },
          }));
          
          const flowEdges = [];
          for (let i = 0; i < flowNodes.length - 1; i++) {
            flowEdges.push({
              id: `e${i}-${i+1}`,
              source: flowNodes[i].id,
              target: flowNodes[i+1].id,
              type: 'smoothstep',
            });
          }
          
          setNodes(flowNodes);
          setEdges(flowEdges);
        } catch (err) {
          setError('Failed to load strategy');
          console.error(err);
        }
      };
      
      fetchStrategy();
    }
  }, [id]);

  const onConnect = useCallback((params) => {
    setEdges((eds) => addEdge(params, eds));
  }, [setEdges]);

  const onNodeClick = useCallback((_, node) => {
    setSelectedNode(node);
  }, []);

  const onAddNode = useCallback((nodeType) => {
    const nodeData = availableNodes.find(n => n.id === nodeType);
    if (nodeData) {
      const newNode = {
        id: nodeData.id,
        type: 'customNode',
        position: { 
          x: Math.random() * 300 + 50, 
          y: Math.random() * 300 + 50 
        },
        data: { label: nodeData.name, nodeData },
      };
      
      setNodes((nds) => [...nds, newNode]);
    }
  }, [availableNodes, setNodes]);

  const onSaveStrategy = useCallback(async () => {
    try {
      // Validate
      if (!strategyName) {
        setError('Strategy name is required');
        return;
      }
      
      if (nodes.length === 0) {
        setError('At least one node is required');
        return;
      }
      
      // Convert flow to chain strategy
      const sortedNodes = topologicalSort(nodes, edges);
      if (!sortedNodes) {
        setError('Invalid flow: contains cycles');
        return;
      }
      
      const strategyNodes = sortedNodes.map(node => node.id);
      
      // Create strategy object
      const strategy = {
        name: strategyName,
        description: strategyDescription,
        nodes: strategyNodes,
      };
      
      // Save to API
      let result;
      if (id) {
        result = await chainService.updateStrategy(id, strategy);
      } else {
        result = await chainService.createStrategy(strategy);
      }
      
      // Navigate to strategy list
      navigate('/strategies');
    } catch (error) {
      setError(`Failed to save strategy: ${error.message}`);
      console.error(error);
    }
  }, [nodes, edges, strategyName, strategyDescription, id, navigate]);

  return (
    <Box sx={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Box sx={{ mb: 2 }}>
        <TextField
          label="Strategy Name"
          value={strategyName}
          onChange={(e) => setStrategyName(e.target.value)}
          fullWidth
          margin="normal"
        />
        <TextField
          label="Strategy Description"
          value={strategyDescription}
          onChange={(e) => setStrategyDescription(e.target.value)}
          fullWidth
          multiline
          rows={2}
          margin="normal"
        />
      </Box>
      
      <Box sx={{ display: 'flex', flex: 1 }}>
        <Box sx={{ width: 200, overflow: 'auto', p: 1, borderRight: 1, borderColor: 'divider' }}>
          <Typography variant="h6">Nodes</Typography>
          <NodePalette nodes={availableNodes} onAddNode={onAddNode} />
        </Box>
        
        <Box sx={{ flex: 1 }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </Box>
        
        {selectedNode && (
          <Box sx={{ width: 300, overflow: 'auto', p: 1, borderLeft: 1, borderColor: 'divider' }}>
            <NodeConfigPanel node={selectedNode} />
          </Box>
        )}
      </Box>
      
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={onSaveStrategy}
        >
          {id ? 'Update Strategy' : 'Save Strategy'}
        </Button>
      </Box>
    </Box>
  );
}

export default ChainDesigner;
```

### 14.4 Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    container_name: chain-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-chain_processor}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-chain_processor}"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgbouncer:
    image: edoburu/pgbouncer:1.18
    container_name: chain-pgbouncer
    environment:
      - DB_USER=${POSTGRES_USER:-postgres}
      - DB_PASSWORD=${POSTGRES_PASSWORD:-postgres}
      - DB_HOST=postgres
      - DB_NAME=${POSTGRES_DB:-chain_processor}
      - POOL_MODE=transaction
      - MAX_CLIENT_CONN=100
      - DEFAULT_POOL_SIZE=20
    ports:
      - "6432:5432"
    depends_on:
      postgres:
        condition: service_healthy

  api:
    build: 
      context: ../chain-processor-api
    container_name: chain-api
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@pgbouncer:5432/${POSTGRES_DB:-chain_processor}
      - SECRET_KEY=${SECRET_KEY:-dev_secret_key}
      - ENVIRONMENT=${ENVIRONMENT:-development}
      - CORS_ORIGINS=http://api:8000,http://localhost:3000
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      pgbouncer:
        condition: service_started
    volumes:
      - ../chain-processor-api/src:/app/src

  executor:
    build:
      context: ../chain-processor-executor
    container_name: chain-executor
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@pgbouncer:5432/${POSTGRES_DB:-chain_processor}
      - API_URL=http://api:8000
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317
    depends_on:
      - api
      - pgbouncer
    volumes:
      - ../chain-processor-executor/src:/app/src

  web:
    build:
      context: ../chain-processor-web
    container_name: chain-web
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://api:8000/api
    volumes:
      - ../chain-processor-web/src:/app/src
      - ../chain-processor-web/public:/app/public
    depends_on:
      - api

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ../chain-processor-deployment/observability/prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3001:3000"
    volumes:
      - ../chain-processor-deployment/observability/grafana/provisioning:/etc/grafana/provisioning
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false

  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: jaeger
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
    environment:
      - COLLECTOR_OTLP_ENABLED=true

  loki:
    image: grafana/loki:latest
    container_name: loki
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    volumes:
      - ../chain-processor-deployment/observability/promtail:/etc/promtail
      - /var/log:/var/log
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki

volumes:
  postgres-data:
  prometheus-data:
  grafana-data:
```

## 15. SOLID and DRY Principles Implementation

### 15.1 SOLID Principles

#### Single Responsibility Principle

- Each repository has a clear, focused purpose
- Services are divided by functional responsibility
- Classes have well-defined roles (e.g., repositories, services, controllers)

Example:

```python
# Single responsibility for chain repository
class ChainRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, strategy_id: uuid.UUID) -> Optional[ChainStrategy]:
        """Get a chain strategy by ID."""
        return self.db.query(ChainStrategy).filter(ChainStrategy.id == strategy_id).first()
    
    # Other chain-related data access methods
```

#### Open/Closed Principle

- Node system is extensible without modifying core code
- Strategy patterns allow for different execution approaches
- Plugin architecture for chain nodes

Example:

```python
# Base node class that can be extended without modifying
class ChainNode(ABC):
    @abstractmethod
    def process(self, input_text: str) -> str:
        """Process the input text and return the transformed output."""
        pass
        
    @classmethod
    def validate_input(cls, input_text: str) -> None:
        """Validate the input text."""
        if not isinstance(input_text, str):
            raise InvalidInputError("Input must be a string")
        if not input_text:
            raise InvalidInputError("Input cannot be empty")
```

#### Liskov Substitution Principle

- Clear exception inheritance hierarchy
- Base classes with well-defined contracts
- Appropriate use of composition for models where inheritance is not suitable

Example:

```python
# Base exception hierarchy
class ChainProcessorError(Exception):
    """Base exception for chain processor errors."""
    pass

class StrategyLoadError(ChainProcessorError):
    """Raised when a strategy cannot be loaded."""
    pass

class NodeNotFoundError(ChainProcessorError):
    """Raised when a node is not found."""
    pass
```

#### Interface Segregation Principle

- Clean API boundaries between services
- Focused repositories with specific data access methods
- Well-defined Pydantic models for different use cases

Example:

```python
# Separate models for different use cases
class NodeBase(BaseModel):
    """Base model for node data."""
    name: str
    description: Optional[str] = None

class NodeCreate(NodeBase):
    """Model for creating a new node."""
    code: str

class Node(NodeBase):
    """Full node model with metadata."""
    id: UUID4
    code: str
    created_at: datetime
    updated_at: datetime
    created_by: UUID4
    version: int
```

#### Dependency Inversion Principle

- Services depend on abstractions (repositories, interfaces)
- Dependency injection throughout the codebase
- Core library defines interfaces implemented by concrete services

Example:

```python
# Dependency injection
@router.post("/", response_model=Strategy)
def create_chain(
    chain: StrategyCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Create a new chain strategy."""
    chain_repo = ChainRepository(db)  # Repository injected via dependency
    # Implementation
```

### 15.2 DRY (Don't Repeat Yourself)

#### Shared Core Library

- Common models, exceptions, and utilities in one place
- Consistent data validation using Pydantic

#### Repository Pattern

- Encapsulated database operations
- Reusable data access methods

#### Consistent API Structure

- Similar endpoints follow the same patterns
- Reusable error handling

#### Shared UI Components

- Common UI elements for consistent experience
- Reusable form components

## 16. Development Workflow

For local development:

1. Clone all repositories into a single parent directory
2. Use the docker-compose.yml from the deployment repository
3. Run services in development mode with volume mounts for local code changes

```bash
# Example development workflow
git clone https://github.com/chain-processor-org/chain-processor-core.git
git clone https://github.com/chain-processor-org/chain-processor-db.git
git clone https://github.com/chain-processor-org/chain-processor-api.git
git clone https://github.com/chain-processor-org/chain-processor-executor.git
git clone https://github.com/chain-processor-org/chain-processor-web.git
git clone https://github.com/chain-processor-org/chain-processor-deployment.git

cd chain-processor-deployment
cp .env.example .env
# Edit .env as needed
docker-compose up -d
```

## 17. Appendices

### Appendix A: Architecture Diagram

```txt
┌───────────────────────────────────────────────────────────────────┐
│                   Client (Browser/External Service)                │
└───────────────┬───────────────────────────────────┬───────────────┘
                │                                   │
                ▼                                   ▼
┌───────────────────────────┐             ┌───────────────────────┐
│        Web UI (React)     │             │    API (FastAPI)      │
│                           │◄────────────┤                       │
│  - Chain Designer         │             │  - REST API           │
│  - Execution Monitor      │             │  - WebSocket          │
│  - Admin Interface        │             │  - Authentication     │
└───────────────────────────┘             └─────────┬─────────────┘
                                                    │
                                                    ▼
┌──────────────────────────────────────────────────────────────────┐
│                          Executor Service                         │
│                                                                   │
│  - Chain Execution Engine                                         │
│  - Node Loading & Execution                                       │
│  - Metrics Collection                                             │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────┐     ┌───────────────────────────────────────┐
│                     │     │         PostgreSQL Database            │
│  Object Storage     │◄────┤                                        │
│  (Node Backup)      │     │  - Chain Definitions                   │
│                     │     │  - Node Code (Primary Storage)         │
└─────────────────────┘     │  - Execution History                   │
                            │  - User Management                     │
                            │  - Metrics                             │
                            └───────────────────────────────────────┘
```

### Appendix B: Node Development Guidelines

#### B.1 Node Structure

- Nodes must be pure functions that take a string input and return a string output
- Nodes must validate their input
- Nodes must handle errors gracefully
- Nodes should be deterministic for the same input (but may have side effects through out-of-band hooks)

#### B.2 Node Code Example

```python
def node(input_text: str) -> str:
    """
    Example node that capitalizes the input text.
    
    Args:
        input_text: The input text to process
        
    Returns:
        The capitalized text
        
    Raises:
        InvalidInputError: If the input is invalid
    """
    # Validate input
    if not isinstance(input_text, str):
        raise InvalidInputError("Input must be a string")
    if not input_text:
        raise InvalidInputError("Input cannot be empty")
    
    # Process input
    return input_text.upper()
```

#### B.3 Side Effects in Nodes

While node processing should be deterministic and pure for the same inputs, in some cases (such as A/B testing or ML model inference), it may be necessary to record side effects. To do this properly:

1. Node processing (the actual transformation of input to output) should remain pure.
2. Side effects should be recorded through separate hooks or callbacks.
3. Documentation should clearly indicate when a node has side effects.

Example with side effect:

```python
def node(input_text: str) -> str:
    """
    Example node that counts words and records metrics.
    
    This node has side effects: increments word count metrics.
    
    Args:
        input_text: The input text to process
        
    Returns:
        The input text with word count prepended
        
    Raises:
        InvalidInputError: If the input is invalid
    """
    # Validate input
    if not isinstance(input_text, str):
        raise InvalidInputError("Input must be a string")
    if not input_text:
        raise InvalidInputError("Input cannot be empty")
    
    # Process input (pure transformation)
    word_count = len(input_text.split())
    result = f"Word count: {word_count}\n\n{input_text}"
    
    # Record side effect through separate hook
    try:
        import metrics
        metrics.increment("word_count", word_count)
    except ImportError:
        # Side effect failed, but node processing continues
        pass
    
    return result
```

### Appendix C: ADR Template

```markdown
# ADR-{NUMBER}: {TITLE}

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[Description of the issue/situation that the ADR addresses]

## Decision
[Description of the decision that was made]

## Consequences
[Description of the resulting context after applying the decision]

## Alternatives Considered
[Description of alternative options that were considered]

## References
[Links to related resources]

---

*End of Specification v1.2*
