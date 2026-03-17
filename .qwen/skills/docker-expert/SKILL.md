---
name: docker-expert
description: Docker containerization expert with deep knowledge of multi-stage builds, image optimization, container security, Docker Compose orchestration, and production deployment patterns.
---

# Docker Expert Skill

## Purpose

This skill provides complete Docker expertise for containerizing the Customer Success AI agent with optimized multi-stage builds, security best practices, and Docker Compose orchestration for local development and production deployment.

## When to Use This Skill

Use this skill when you need to:
- Create optimized Dockerfiles for Python applications
- Implement multi-stage builds for smaller images
- Configure Docker Compose for local development
- Apply container security best practices
- Optimize image size and build time
- Set up health checks and resource limits
- Configure container networking
- Deploy containers to production

---

## Multi-Stage Dockerfile

```dockerfile
# Dockerfile

# =============================================================================
# Stage 1: Base Image with Common Dependencies
# =============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# =============================================================================
# Stage 2: Builder - Install Python Dependencies
# =============================================================================
FROM base as builder

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 3: Production Runtime
# =============================================================================
FROM base as production

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Set PATH to include user packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "workers.runner"]

# =============================================================================
# Stage 4: Development Image (optional)
# =============================================================================
FROM production as development

# Install development dependencies
COPY requirements-dev.txt .
RUN pip install --user --no-cache-dir -r requirements-dev.txt

# Enable hot reload
ENV PYTHONUNBUFFERED=1

# Switch back to root for development tools if needed
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

USER appuser

# Default command for development
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

## Docker Compose for Local Development

```yaml
# docker-compose.yml

version: '3.8'

services:
  # =============================================================================
  # PostgreSQL Database with pgvector
  # =============================================================================
  postgres:
    image: pgvector/pgvector:pg16
    container_name: fte_postgres
    environment:
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-secure_password_here}
      POSTGRES_DB: customer_success_fte
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app_user -d customer_success_fte"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - fte_network

  # =============================================================================
  # Kafka for Event Streaming
  # =============================================================================
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: fte_zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - fte_network

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: fte_kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    volumes:
      - kafka_data:/var/lib/kafka/data
    networks:
      - fte_network

  # =============================================================================
  # FastAPI Application
  # =============================================================================
  api:
    build:
      context: .
      dockerfile: Dockerfile
      target: development
    container_name: fte_api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://app_user:${DB_PASSWORD:-secure_password_here}@postgres:5432/customer_success_fte
      - KAFKA_BOOTSTRAP_SERVERS=kafka:29092
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=DEBUG
    volumes:
      - .:/app
    depends_on:
      postgres:
        condition: service_healthy
      kafka:
        condition: service_started
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - fte_network

  # =============================================================================
  # Worker Processors
  # =============================================================================
  worker:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: fte_worker
    environment:
      - DATABASE_URL=postgresql://app_user:${DB_PASSWORD:-secure_password_here}@postgres:5432/customer_success_fte
      - KAFKA_BOOTSTRAP_SERVERS=kafka:29092
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      kafka:
        condition: service_started
    command: python -m workers.runner
    deploy:
      replicas: 2
    networks:
      - fte_network

  # =============================================================================
  # Kafka UI (Optional - for development)
  # =============================================================================
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: fte_kafka_ui
    depends_on:
      - kafka
    ports:
      - "8090:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: fte-cluster
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:29092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
    networks:
      - fte_network

  # =============================================================================
  # pgAdmin (Optional - for development)
  # =============================================================================
  pgadmin:
    image: dpage/pgadmin4
    container_name: fte_pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@techcorp.com
      PGADMIN_DEFAULT_PASSWORD: admin_password
    ports:
      - "8080:80"
    depends_on:
      - postgres
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    networks:
      - fte_network

volumes:
  postgres_data:
    driver: local
  kafka_data:
    driver: local
  pgadmin_data:
    driver: local

networks:
  fte_network:
    driver: bridge
```

---

## Requirements Files

```txt
# requirements.txt

# Core Dependencies
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# OpenAI
openai-agents==0.0.1
openai==1.10.0

# Kafka
aiokafka==0.9.0

# PostgreSQL
asyncpg==0.29.0
psycopg2-binary==2.9.9
pgvector==0.2.4

# Google APIs (Gmail)
google-api-python-client==2.113.0
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.0
google-cloud-pubsub==2.19.4

# Twilio (WhatsApp)
twilio==8.11.1

# Utilities
python-dotenv==1.0.0
httpx==0.26.0
aiohttp==3.9.1
tenacity==8.2.3

# Monitoring
prometheus-client==0.19.0
```

```txt
# requirements-dev.txt

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0

# Development
black==23.12.1
ruff==0.1.9
mypy==1.8.0

# Debugging
ipdb==0.13.13
```

---

## .dockerignore

```plaintext
# .dockerignore

# Git
.git
.gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
.eggs/

# Virtual environments
venv/
env/
.env
.venv

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Documentation
docs/
*.md
!requirements*.txt

# Logs
logs/
*.log

# Local development
local_data/
tmp/
temp/

# Docker
Dockerfile
docker-compose*.yml
.dockerignore
```

---

## Container Security Best Practices

```dockerfile
# Security-focused Dockerfile additions

# 1. Use specific base image version (not latest)
FROM python:3.11.7-slim

# 2. Install security updates
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get upgrade -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Use non-root user
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# 4. Set read-only filesystem where possible
# (In docker-compose or Kubernetes)

# 5. Drop capabilities
# In docker-compose:
# cap_drop:
#   - ALL
# cap_add:
#   - NET_BIND_SERVICE

# 6. Use secrets for sensitive data
# In docker-compose:
# secrets:
#   - db_password
#   - api_key

# 7. Scan for vulnerabilities
# Run: docker scan <image_name>

# 8. Use distroless or scratch for production
# FROM gcr.io/distroless/python3-debian11
```

---

## Image Optimization Tips

```dockerfile
# 1. Multi-stage builds (shown above)

# 2. Order layers for better caching
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
COPY . .

# 3. Use .dockerignore to reduce context size

# 4. Combine RUN commands to reduce layers
RUN apt-get update && apt-get install -y package1 package2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. Use slim or alpine base images
FROM python:3.11-slim  # Instead of python:3.11

# 6. Remove unnecessary files
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 7. Use specific versions for reproducibility
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
```

---

## Docker Commands Reference

```bash
# Build image
docker build -t customer-success-fte:latest .

# Build with specific target
docker build --target production -t customer-success-fte:prod .

# Run container
docker run -p 8000:8000 --env-file .env customer-success-fte:latest

# Run with volume mount (development)
docker run -v $(pwd):/app -p 8000:8000 customer-success-fte:dev

# View logs
docker logs -f <container_id>

# Execute command in running container
docker exec -it <container_id> bash

# Check image size
docker images customer-success-fte

# Scan for vulnerabilities
docker scan customer-success-fte:latest

# Clean up
docker system prune -a

# Docker Compose
docker-compose up -d           # Start all services
docker-compose down            # Stop all services
docker-compose logs -f         # View logs
docker-compose ps              # List containers
docker-compose build           # Rebuild images
docker-compose restart         # Restart services
```

---

## Acceptance Criteria

- [ ] Multi-stage Dockerfile created
- [ ] Image size optimized (<500MB)
- [ ] Non-root user configured
- [ ] Health checks implemented
- [ ] Docker Compose for local development
- [ ] All services containerized
- [ ] Security best practices applied
- [ ] .dockerignore configured
- [ ] Build caching optimized
- [ ] Production and development targets

## Related Skills

- `k8s-fte-deployment` - Kubernetes deployment from Docker images
- `kafka-event-processing` - Kafka in Docker Compose
- `postgres-crm-schema` - PostgreSQL with pgvector in containers

## References

- [Docker Documentation](https://docs.docker.com/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
