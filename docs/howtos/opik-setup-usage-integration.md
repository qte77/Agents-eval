# Opik Setup and Integration Guide

This document covers the setup, configuration, and integration of Opik -
anopen-source LLM evaluation and tracing platform by Comet ML.

## Overview

Opik provides comprehensive observability for LLM applications through tracing,
evaluation, and monitoring capabilities. It consists of multiple Docker
containers working together to provide a complete platform.

## Quick Start

### Setup Commands

```bash
# Complete setup (recommended for first time)
make setup_dev_full

# Or individual commands:
make start_opik      # Start services only
make setup_opik_env  # Set environment variables only
make status_opik     # Check service health
make stop_opik       # Stop services
make clean_opik      # Remove all data (destructive)
```

### Access Points

After running `make start_opik`, the following services will be available:

- **Frontend**: <http://localhost:5173>
- **Backend API**: <http://localhost:8080>
- **ClickHouse**: <http://localhost:8123>

Additional services:

- **OpenAPI Docs**: <http://localhost:3003>
- **Fluent Bit Logs**: <http://localhost:2020>

## File Structure

### Required Files

```text
/workspaces/Agents-eval/
├── docker-compose.opik.yaml              # Main service definitions
└── opik/
    ├── clickhouse/
    │   └── config.xml                   # ClickHouse configuration
    ├── nginx_default_local.conf         # Frontend reverse proxy config
    └── fluent-bit.conf                  # Logging configuration
```

### Configuration Files

#### ClickHouse Configuration (`opik/clickhouse/config.xml`)

```xml
<clickhouse>
    <!-- Listen on all interfaces for Docker networking -->
    <listen_host>0.0.0.0</listen_host>
    
    <!-- Zookeeper configuration for ReplicatedMergeTree -->
    <zookeeper>
        <node>
            <host>zookeeper</host>
            <port>2181</port>
        </node>
    </zookeeper>
    
    <!-- Remote servers configuration -->
    <remote_servers>
        <opik>
            <shard>
                <replica>
                    <host>clickhouse</host>
                    <port>9000</port>
                </replica>
            </shard>
        </opik>
    </remote_servers>
    
    <!-- Macros for ReplicatedMergeTree tables -->
    <macros>
        <shard>01</shard>
        <replica>opik-single-node</replica>
        <cluster>opik</cluster>
    </macros>
</clickhouse>
```

## Container Architecture

### Data Storage Layer

1. **MySQL** (`agents-eval_mysql_1`)
   - **Purpose**: Primary relational database for application state
   - **Port**: 3306
   - **Stores**: User accounts, projects, workspaces, experiment metadata,
     configuration settings
   - **Why needed**: Structured data with ACID properties for critical
     application state

2. **ClickHouse** (`agents-eval_clickhouse_1`)
   - **Purpose**: Columnar analytics database for high-volume trace data
   - **Ports**: 8123 (HTTP), 9000 (Native)
   - **Stores**: LLM traces, spans, metrics, evaluation results, time-series data
   - **Why needed**: Optimized for analytical queries on large datasets
   - **Engine**: ReplicatedMergeTree tables for distributed coordination

3. **Redis** (`agents-eval_redis_1`)
   - **Purpose**: In-memory cache and session store
   - **Port**: 6379
   - **Stores**: Session data, temporary cache, job queues
   - **Why needed**: Fast access for frequently used data and user sessions

4. **Zookeeper** (`agents-eval_zookeeper_1`)
   - **Purpose**: Distributed coordination service for ClickHouse
   - **Port**: 2181
   - **Manages**: ClickHouse cluster coordination, leader election, configuration
   - **Why needed**: Required for ClickHouse ReplicatedMergeTree table engine

5. **MinIO** (`agents-eval_minio_1`)
   - **Purpose**: S3-compatible object storage
   - **Port**: 9000 (internal)
   - **Stores**: Artifacts, files, binary data, model weights, datasets
   - **Why needed**: Scalable storage for large files that don't fit in databases

### Application Services

1. **Backend** (`agents-eval_backend_1`)
   - **Purpose**: Main REST API server (Java/Spring Boot)
   - **Ports**: 8080 (API), 3003 (OpenAPI docs)
   - **Handles**: Core business logic, API endpoints, authentication, data validation
   - **Why needed**: Primary interface between frontend and data layer

2. **Python Backend** (`agents-eval_python-backend_1`)
   - **Purpose**: Python-specific processing and evaluation engine
   - **Port**: 8000
   - **Handles**: LLM evaluations, Python code execution, ML model inference
   - **Security**: Docker-in-Docker with network restrictions
   - **Configuration**:
     - `PYTHON_CODE_EXECUTOR_CONTAINERS_NUM: 5`
     - `PYTHON_CODE_EXECUTOR_EXEC_TIMEOUT_IN_SECS: 3`
     - `PYTHON_CODE_EXECUTOR_ALLOW_NETWORK: "false"`

3. **Frontend** (`agents-eval_frontend_1`)
   - **Purpose**: Web-based user interface (React + Nginx)
   - **Ports**: 5173 (Web UI), 2020 (Fluent Bit logs)
   - **Provides**: Dashboard, trace visualization, project management UI
   - **Technology**: React with Nginx reverse proxy

### Initialization & Setup

1. **ClickHouse Init** (`agents-eval_clickhouse-init_1`)
   - **Purpose**: One-time configuration setup for ClickHouse
   - **Task**: Copy configuration files from `./opik/clickhouse` to shared volume
   - **Process**: Sets proper permissions (UID 1000) for ClickHouse container
   - **Lifecycle**: Runs once at startup, then exits

2. **MinIO Client** (`agents-eval_mc_1`)
    - **Purpose**: Initialize MinIO storage buckets and policies
    - **Task**: Create buckets, set access permissions, configure policies
    - **Lifecycle**: Runs once at startup, then exits

3. **Demo Data Generator** (`agents-eval_demo-data-generator_1`)
    - **Purpose**: Populate platform with sample traces and data
    - **Task**: Create example projects, traces, evaluations for testing
    - **Lifecycle**: Optional, runs once then exits

### Configuration File Usage

#### ClickHouse Config Flow

```text
Host: /workspaces/Agents-eval/opik/clickhouse/config.xml
  ↓ (volume mount)
Init Container: /clickhouse_config_files/config.xml
  ↓ (copy + chown command)  
Shared Volume: clickhouse-config:/config/config.xml
  ↓ (volume mount)
ClickHouse: /etc/clickhouse-server/config.d/config.xml
  ↓ (ClickHouse reads on startup)
Active Configuration: Merged with default ClickHouse config
```

## Python Integration

### Environment Setup

The `make setup_opik_env` command configures:

```bash
export OPIK_URL_OVERRIDE=http://localhost:8080  # Backend API endpoint
export OPIK_WORKSPACE=peerread-evaluation       # Default workspace
export OPIK_PROJECT_NAME=peerread-evaluation    # Default project
```

### Usage Examples

#### LLM Evaluation Tracing

```python
# src/app/evals/evaluation_pipeline.py
import opik
from opik import track

@track(
    name="peer_review_evaluation",
    tags=["peerread", "evaluation"],
    metadata={"dataset": "peerread", "model": "gpt-4"}
)
def evaluate_paper_review(paper_content: str, review_content: str) -> dict:
    """Evaluate quality of peer review against paper."""
    
    # Track LLM calls within evaluation
    with opik.track("llm_judgment") as span:
        judgment = llm_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Evaluate this peer review..."},
                {"role": "user", "content": f"Paper: {paper_content}\nReview: {review_content}"}
            ]
        )
        span.update(
            input={"paper_length": len(paper_content), "review_length": len(review_content)},
            output={"judgment": judgment.choices[0].message.content},
            usage=judgment.usage._asdict()
        )
    
    return {"score": 8.5, "feedback": "Thorough review with constructive feedback"}
```

#### Agent System Tracing

```python
# src/app/agent_system.py
import opik
from opik import track

@track(name="agent_execution", tags=["pydantic-ai", "agent"])
def run_agent_evaluation(prompt: str, model_name: str) -> str:
    """Track PydanticAI agent execution."""
    
    with opik.track("agent_planning") as span:
        plan = agent.plan(prompt)
        span.update(input={"prompt": prompt}, output={"plan": plan})
    
    with opik.track("agent_execution") as span:
        result = agent.run(plan, model=model_name)
        span.update(
            input={"plan": plan, "model": model_name},
            output={"result": result},
            metadata={"execution_time": span.end_time - span.start_time}
        )
    
    return result
```

#### Model Comparison Experiments

```python
# src/app/experiments/model_comparison.py
import opik

def compare_models_on_peerread():
    """Compare different LLMs on PeerRead evaluation task."""
    
    experiment = opik.create_experiment(
        name="peerread_model_comparison",
        description="Compare GPT-4 vs Claude vs Gemini on peer review evaluation"
    )
    
    models = ["gpt-4", "claude-3-sonnet", "gemini-pro"]
    
    for model in models:
        with opik.track(f"model_evaluation_{model}") as span:
            results = evaluate_with_model(model, test_dataset)
            
            # Log metrics
            span.log_metric("accuracy", results["accuracy"])
            span.log_metric("f1_score", results["f1"])
            span.log_metric("avg_latency", results["latency"])
            
            experiment.log_traces([span])
```

## Problems Encountered and Solutions

### 1. ClickHouse Networking Issues

**Problem**: ClickHouse exit code 210 (Connection refused)

- **Cause**: ClickHouse couldn't bind to network interfaces in Docker environment
- **Solution**: Added `<listen_host>0.0.0.0</listen_host>` to allow Docker container
  networking
- **File**: `opik/clickhouse/config.xml`

### 2. Zookeeper Integration

**Problem**: "Can't create replicated table without ZooKeeper (NO_ZOOKEEPER)" error

- **Cause**: ClickHouse ReplicatedMergeTree tables require Zookeeper coordination
- **Solution**: Added Zookeeper configuration block to ClickHouse config
- **Result**: ClickHouse successfully connected to Zookeeper for coordination

### 3. Cluster Configuration

**Problem**: "Requested cluster 'opik' not found (CLUSTER_DOESNT_EXIST)" error

- **Cause**: ClickHouse needed cluster definition for distributed operations
- **Solution**: Added `<remote_servers>` configuration defining the 'opik' cluster
- **Impact**: Backend could now use distributed table operations

### 4. Frontend 502 Bad Gateway

**Problem**: Port 5173 showing "502 Bad Gateway" error

- **Cause**: Frontend couldn't start due to unhealthy backend dependencies
- **Solution**: Fixed all backend services (ClickHouse, MySQL, Redis, Zookeeper)
- **Result**: Frontend became healthy and accessible

### 5. File Structure Reorganization

**Problem**: Complex nested directory structure (`scripts/worktrees/opik/`)

- **Solution**: Moved all configuration files to clean `opik/` directory
- **Updated**: Docker Compose volume paths to use new structure
- **Result**: Simplified maintenance and clearer organization

### 6. Environment Variable Configuration

**Problem**: Incorrect API endpoint in `OPIK_URL_OVERRIDE`

- **Issue**: Was pointing to port 3003 (OpenAPI docs) instead of 8080 (API)
- **Solution**: Fixed Makefile to use correct backend API port (8080)
- **Impact**: Python SDK now correctly sends traces to local Opik instance

## Network Architecture

```text
Frontend (5173) → Nginx → Backend API (8080)
                       ↓
Backend → MySQL (3306) + ClickHouse (8123) + Redis (6379)
       ↓
ClickHouse ↔ Zookeeper (2181)
Backend → MinIO (9000) for artifacts
Python Backend (8000) ← Backend
```

## Benefits for This Project

- **Debug evaluation failures**: See exactly where evaluations fail
- **Compare model performance**: Track metrics across different LLMs
- **Monitor costs**: Track token usage and API costs
- **Reproduce results**: Full trace history for research reproducibility
- **Team collaboration**: Share evaluation results via Opik UI
- **Performance optimization**: Identify bottlenecks in evaluation pipeline

## Maintenance

### Health Checks

```bash
# Check all services
make status_opik

# Check specific service
docker-compose -f docker-compose.opik.yaml ps clickhouse
```

### Logs

```bash
# View all logs
docker-compose -f docker-compose.opik.yaml logs

# View specific service logs
docker-compose -f docker-compose.opik.yaml logs backend
```

### Data Cleanup

```bash
# WARNING: Destroys all trace data
make clean_opik
```

## Resources

- **Official Opik Repository**: <https://github.com/comet-ml/opik>
- **Official Docker Compose**: <https://github.com/comet-ml/opik/blob/main/deployment/docker-compose/docker-compose.yaml>
- **Documentation**: <https://www.comet.com/docs/opik/>
- **Local Deployment Guide**: <https://www.comet.com/docs/opik/self-host/local_deployment/>
- **Python SDK**: `pip install opik`

## Summary

Opik provides a comprehensive LLM observability platform with 11 Docker
containers working together. The setup includes data storage (MySQL,
ClickHouse, Redis), coordination (Zookeeper), object storage (MinIO),
application services (Backend, Python Backend, Frontend), and initialization
containers. The platform integrates seamlessly with Python applications for
LLM evaluation and tracing workflows.
