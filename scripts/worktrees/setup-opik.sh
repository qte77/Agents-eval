#!/bin/bash
# Official Opik Local Deployment Setup
# Reference: https://www.comet.com/docs/opik/self-host/local_deployment/

set -e

echo "🔧 Setting up Official Opik Local Deployment"

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed. Please install Docker Compose first."
    exit 1
fi

# Create docker-compose.opik.yml based on official repository
echo "📝 Creating official Opik Docker Compose configuration..."

cat > docker-compose.opik.yml << 'EOF'
# Official Opik Local Deployment with ClickHouse Analytics
# Reference: https://github.com/comet-ml/opik/blob/main/deployment/docker-compose/docker-compose.yaml

version: '3.8'

services:
  # ClickHouse for analytics and tracing data storage
  clickhouse:
    image: clickhouse/clickhouse-server:24.3
    container_name: opik-clickhouse
    ports:
      - "8123:8123"  # HTTP interface
      - "9000:9000"  # Native interface
    environment:
      - CLICKHOUSE_USER=opik
      - CLICKHOUSE_PASSWORD=opik123
      - CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1
    volumes:
      - clickhouse_data:/var/lib/clickhouse
      - ./scripts/worktrees/opik/clickhouse-init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "clickhouse-client --user=opik --password=opik123 --query='SELECT 1'"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # Redis for caching and session management
  redis:
    image: redis:7-alpine
    container_name: opik-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # Opik Backend API
  opik-backend:
    image: comet/opik-backend:latest
    container_name: opik-backend
    ports:
      - "3003:3003"
    environment:
      - CLICKHOUSE_URL=clickhouse://opik:opik123@clickhouse:9000/opik
      - REDIS_URL=redis://redis:6379
      - OPIK_DATABASE_URL=clickhouse://opik:opik123@clickhouse:9000/opik
    depends_on:
      clickhouse:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:3003/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Opik Frontend UI
  opik-frontend:
    image: comet/opik-frontend:latest
    container_name: opik-frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_OPIK_API_URL=http://localhost:3003
    depends_on:
      opik-backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:5173 || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  clickhouse_data:
    driver: local
  redis_data:
    driver: local

networks:
  default:
    name: opik-network
EOF

# Create ClickHouse initialization SQL
echo "📝 Creating ClickHouse initialization script..."
mkdir -p scripts/worktrees/opik

cat > scripts/worktrees/opik/clickhouse-init.sql << 'EOF'
-- ClickHouse initialization for Opik
-- Creates database and tables for agent tracing analytics

CREATE DATABASE IF NOT EXISTS opik;

USE opik;

-- Agent execution traces table
CREATE TABLE IF NOT EXISTS agent_traces (
    trace_id String,
    agent_name String,
    agent_role String,
    execution_phase String,
    start_time DateTime64(3),
    end_time DateTime64(3),
    duration_ms UInt64,
    status String,
    metadata String,
    created_at DateTime64(3) DEFAULT now64(3)
) ENGINE = MergeTree()
ORDER BY (created_at, trace_id);

-- Evaluation metrics table  
CREATE TABLE IF NOT EXISTS evaluation_metrics (
    evaluation_id String,
    tier UInt8,
    metric_name String,
    metric_value Float64,
    execution_time_ms UInt64,
    paper_length UInt32,
    review_length UInt32,
    created_at DateTime64(3) DEFAULT now64(3)
) ENGINE = MergeTree()
ORDER BY (created_at, evaluation_id);

-- Graph analysis results
CREATE TABLE IF NOT EXISTS graph_metrics (
    trace_id String,
    node_count UInt32,
    edge_count UInt32,
    complexity_score Float64,
    centrality_measures String,
    coordination_quality Float64,
    created_at DateTime64(3) DEFAULT now64(3)
) ENGINE = MergeTree()
ORDER BY (created_at, trace_id);

-- Performance analytics view
CREATE VIEW IF NOT EXISTS agent_performance AS
SELECT 
    agent_role,
    agent_name,
    count() as execution_count,
    avg(duration_ms) as avg_duration_ms,
    quantile(0.95)(duration_ms) as p95_duration_ms,
    sum(status = 'success') / count() as success_rate
FROM agent_traces
WHERE created_at >= now() - INTERVAL 7 DAY
GROUP BY agent_role, agent_name
ORDER BY avg_duration_ms DESC;
EOF

# Create environment configuration
echo "📝 Creating Opik environment configuration..."

cat > .env.opik << 'EOF'
# Opik Local Deployment Environment Variables

# Opik Configuration
OPIK_URL_OVERRIDE=http://localhost:3003
OPIK_WORKSPACE=default
OPIK_PROJECT_NAME=agents-eval
OPIK_LOG_START_TRACE_SPAN=true

# ClickHouse Configuration
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=opik
CLICKHOUSE_PASSWORD=opik123
CLICKHOUSE_DATABASE=opik

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Development Settings
OPIK_BATCH_SIZE=100
OPIK_TIMEOUT_SECONDS=30
OPIK_EXPORT_INTERVAL=5
EOF

echo "✅ Opik configuration files created successfully!"
echo ""
echo "🚀 To start Opik stack:"
echo "   make start_opik"
echo ""
echo "🌐 Services will be available at:"
echo "   • Opik UI: http://localhost:5173"
echo "   • Opik API: http://localhost:3003"  
echo "   • ClickHouse: http://localhost:8123"
echo "   • Redis: localhost:6379"
echo ""
echo "📊 To connect from Python:"
echo "   export OPIK_URL_OVERRIDE=http://localhost:3003"
echo "   export OPIK_WORKSPACE=default"
echo "   export OPIK_PROJECT_NAME=agents-eval"