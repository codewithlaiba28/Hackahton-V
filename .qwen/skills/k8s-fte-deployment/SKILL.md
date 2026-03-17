---
name: k8s-fte-deployment
description: Deploy Customer Success FTE on Kubernetes with auto-scaling workers, Docker multi-stage builds, ConfigMaps, Secrets, Services, Ingress, and production-ready deployment manifests.
---

# Kubernetes FTE Deployment Skill

## Purpose

This skill provides complete Kubernetes deployment manifests for running a Customer Success AI agent at scale with auto-scaling workers, proper resource management, health checks, and production-grade configurations.

## When to Use This Skill

Use this skill when you need to:
- Deploy the Customer Success FTE on Kubernetes
- Auto-scale worker pods based on Kafka lag
- Manage configuration with ConfigMaps and Secrets
- Set up health checks and readiness probes
- Configure horizontal pod autoscaling (HPA)
- Deploy with rolling updates and zero downtime
- Monitor pod health and resource usage
- Set up ingress for webhook endpoints

---

## Kubernetes Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KUBERNETES CLUSTER                                    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         NAMESPACE: customer-success                  │    │
│  │                                                                      │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │    │
│  │  │   API Service    │  │  Gmail Webhook   │  │ WhatsApp Webhook │   │    │
│  │  │   (FastAPI)      │  │   Endpoint       │  │   Endpoint       │   │    │
│  │  │  :8000           │  │   :8001          │  │   :8002          │   │    │
│  │  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘   │    │
│  │           │                     │                     │              │    │
│  │           └─────────────────────┼─────────────────────┘              │    │
│  │                                 │                                    │    │
│  │                                 ▼                                    │    │
│  │                      ┌─────────────────────┐                         │    │
│  │                      │   Ingress Controller │                         │    │
│  │                      └─────────────────────┘                         │    │
│  │                                                                      │    │
│  │  ┌──────────────────────────────────────────────────────────────┐    │    │
│  │  │                    Worker Deployments                         │    │    │
│  │  │                                                               │    │    │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │    │    │
│  │  │  │  Worker Pod │  │  Worker Pod │  │  Worker Pod │           │    │    │
│  │  │  │  (Agent +   │  │  (Agent +   │  │  (Agent +   │           │    │    │
│  │  │  │  Kafka)     │  │  Kafka)     │  │  Kafka)     │           │    │    │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘           │    │    │
│  │  │       ▲                  ▲                  ▲                 │    │    │
│  │  │       │                  │                  │                 │    │    │
│  │  │       └──────────────────┼──────────────────┘                 │    │    │
│  │  │                          │                                    │    │    │
│  │  │              Horizontal Pod Autoscaler (HPA)                  │    │    │
│  │  │              Min: 2 | Max: 20 | Target: 70% CPU               │    │    │
│  │  └──────────────────────────────────────────────────────────────┘    │    │
│  │                                                                      │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │    │
│  │  │   PostgreSQL     │  │     Kafka        │  │    Redis         │   │    │
│  │  │   StatefulSet    │  │   StatefulSet    │  │   (Cache)       │   │    │
│  │  │   (pgvector)     │  │   (3 brokers)    │  │                 │   │    │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘   │    │
│  │                                                                      │    │
│  │  ┌──────────────────┐  ┌──────────────────┐                         │    │
│  │  │   ConfigMaps     │  │    Secrets       │                         │    │
│  │  │   - app-config   │  │   - db-creds     │                         │    │
│  │  │   - kafka-config │  │   - api-keys     │                         │    │
│  │  └──────────────────┘  └──────────────────┘                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Namespace

```yaml
# k8s/namespace.yaml

apiVersion: v1
kind: Namespace
metadata:
  name: customer-success
  labels:
    app: customer-success-fte
    environment: production
```

---

## ConfigMaps

```yaml
# k8s/configmap.yaml

apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: customer-success
data:
  # Application Configuration
  APP_NAME: "customer-success-fte"
  APP_ENV: "production"
  LOG_LEVEL: "INFO"
  
  # Database Configuration
  DB_HOST: "postgres-service"
  DB_PORT: "5432"
  DB_NAME: "customer_success_fte"
  DB_POOL_MIN_SIZE: "5"
  DB_POOL_MAX_SIZE: "20"
  
  # Kafka Configuration
  KAFKA_BOOTSTRAP_SERVERS: "kafka-0.kafka-headless:9092,kafka-1.kafka-headless:9092,kafka-2.kafka-headless:9092"
  KAFKA_TOPIC_INGRESS: "support-ingress"
  KAFKA_TOPIC_RESPONSES: "support-responses"
  KAFKA_TOPIC_DLQ: "support-dead-letter"
  KAFKA_CONSUMER_GROUP_ID: "support-processor-group"
  KAFKA_MAX_POLL_RECORDS: "10"
  
  # Agent Configuration
  AGENT_MODEL: "gpt-4"
  AGENT_MAX_TOKENS: "1024"
  AGENT_TEMPERATURE: "0.7"
  
  # Channel Configuration
  EMAIL_ENABLED: "true"
  WHATSAPP_ENABLED: "true"
  WEB_FORM_ENABLED: "true"
  
  # Performance Configuration
  RESPONSE_TIMEOUT_SECONDS: "30"
  MAX_CONCURRENT_REQUESTS: "50"
  
  # Metrics Configuration
  METRICS_ENABLED: "true"
  METRICS_PORT: "9090"
```

```yaml
# k8s/kafka-config.yaml

apiVersion: v1
kind: ConfigMap
metadata:
  name: kafka-config
  namespace: customer-success
data:
  # Kafka Topics
  KAFKA_TOPIC_INGRESS: "support-ingress"
  KAFKA_TOPIC_RESPONSES: "support-responses"
  KAFKA_TOPIC_DLQ: "support-dead-letter"
  KAFKA_TOPIC_METRICS: "support-metrics"
  
  # Kafka Consumer Settings
  KAFKA_AUTO_OFFSET_RESET: "earliest"
  KAFKA_ENABLE_AUTO_COMMIT: "false"
  KAFKA_SESSION_TIMEOUT_MS: "30000"
  KAFKA_HEARTBEAT_INTERVAL_MS: "10000"
  KAFKA_MAX_POLL_INTERVAL_MS: "300000"
  
  # Kafka Producer Settings
  KAFKA_PRODUCER_ACKS: "all"
  KAFKA_PRODUCER_RETRIES: "3"
  KAFKA_PRODUCER_BATCH_SIZE: "16384"
  KAFKA_PRODUCER_LINGER_MS: "5"
```

---

## Secrets

```yaml
# k8s/secrets.yaml

apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
  namespace: customer-success
type: Opaque
stringData:
  DB_USER: "app_user"
  DB_PASSWORD: "your-secure-password-here"  # Use external secret management in production
  DB_CONNECTION_STRING: "postgresql://app_user:your-secure-password-here@postgres-service:5432/customer_success_fte"

---
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
  namespace: customer-success
type: Opaque
stringData:
  # OpenAI API Key
  OPENAI_API_KEY: "sk-your-openai-api-key-here"
  
  # Gmail API Credentials (base64 encoded credentials.json)
  GOOGLE_CREDENTIALS: |
    {
      "type": "service_account",
      "project_id": "your-project",
      "private_key_id": "...",
      "private_key": "-----BEGIN PRIVATE KEY-----\n...",
      "client_email": "...",
      "client_id": "...",
      "auth_uri": "...",
      "token_uri": "..."
    }
  
  # Twilio Credentials
  TWILIO_ACCOUNT_SID: "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  TWILIO_AUTH_TOKEN: "your-auth-token-here"
  TWILIO_WHATSAPP_NUMBER: "whatsapp:+14155238886"
  
  # SMTP Credentials
  SMTP_USER: "notifications@techcorp.com"
  SMTP_PASSWORD: "your-smtp-password-here"
```

**Note:** In production, use external secret management like:
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Sealed Secrets for GitOps

---

## Dockerfile (Multi-stage)

```dockerfile
# Dockerfile

# =============================================================================
# Stage 1: Builder
# =============================================================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.11-slim as runtime

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "workers.runner"]
```

---

## Requirements.txt

```txt
# requirements.txt

# Core Dependencies
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# OpenAI Agents SDK
openai-agents==0.0.1
openai==1.10.0

# Kafka
aiokafka==0.9.0

# PostgreSQL
asyncpg==0.29.0
psycopg2-binary==2.9.9

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

# Monitoring
prometheus-client==0.19.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
```

---

## Worker Deployment

```yaml
# k8s/worker-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker-deployment
  namespace: customer-success
  labels:
    app: worker
    component: message-processor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: worker
      component: message-processor
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: worker
        component: message-processor
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
    spec:
      serviceAccountName: customer-success-sa
      terminationGracePeriodSeconds: 60
      containers:
      - name: worker
        image: techcorp/customer-success-fte:latest
        imagePullPolicy: Always
        command: ["python", "-m", "workers.runner"]
        ports:
        - containerPort: 9090
          name: metrics
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        envFrom:
        - configMapRef:
            name: app-config
        - configMapRef:
            name: kafka-config
        - secretRef:
            name: db-credentials
        - secretRef:
            name: api-keys
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        volumeMounts:
        - name: tmp-volume
          mountPath: /tmp
      volumes:
      - name: tmp-volume
        emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchLabels:
                  app: worker
              topologyKey: kubernetes.io/hostname
```

---

## Horizontal Pod Autoscaler (HPA)

```yaml
# k8s/hpa.yaml

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: worker-hpa
  namespace: customer-success
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: worker-deployment
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
      - type: Pods
        value: 4
        periodSeconds: 60
      selectPolicy: Max
```

---

## API Service Deployment

```yaml
# k8s/api-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
  namespace: customer-success
  labels:
    app: api
    component: fastapi
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
      component: fastapi
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: api
        component: fastapi
    spec:
      containers:
      - name: api
        image: techcorp/customer-success-fte:latest
        imagePullPolicy: Always
        command: ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
        ports:
        - containerPort: 8000
          name: http
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: api-keys
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: customer-success
spec:
  selector:
    app: api
    component: fastapi
  ports:
  - port: 8000
    targetPort: 8000
    name: http
  type: ClusterIP
```

---

## Ingress

```yaml
# k8s/ingress.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: customer-success-ingress
  namespace: customer-success
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - support.techcorp.com
    secretName: support-tls-secret
  rules:
  - host: support.techcorp.com
    http:
      paths:
      # Web Form
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8000
      
      # Gmail Webhook
      - path: /webhooks/gmail
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8000
      
      # WhatsApp Webhook
      - path: /webhooks/whatsapp
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8000
      
      # API endpoints
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8000
      
      # Health checks
      - path: /health
        pathType: Exact
        backend:
          service:
            name: api-service
            port:
              number: 8000
```

---

## Service Account and RBAC

```yaml
# k8s/rbac.yaml

apiVersion: v1
kind: ServiceAccount
metadata:
  name: customer-success-sa
  namespace: customer-success
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: customer-success-role
  namespace: customer-success
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: customer-success-rolebinding
  namespace: customer-success
subjects:
- kind: ServiceAccount
  name: customer-success-sa
  namespace: customer-success
roleRef:
  kind: Role
  name: customer-success-role
  apiGroup: rbac.authorization.k8s.io
```

---

## Pod Disruption Budget

```yaml
# k8s/pdb.yaml

apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: worker-pdb
  namespace: customer-success
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: worker
      component: message-processor
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-pdb
  namespace: customer-success
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: api
      component: fastapi
```

---

## Network Policy

```yaml
# k8s/network-policy.yaml

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: worker-network-policy
  namespace: customer-success
spec:
  podSelector:
    matchLabels:
      app: worker
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: kafka
    ports:
    - protocol: TCP
      port: 9092
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # For external APIs
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
  namespace: customer-success
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from: []
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: worker
    ports:
    - protocol: TCP
      port: 8000
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

---

## Kustomize Structure

```
k8s/
├── kustomization.yaml
├── namespace.yaml
├── configmap.yaml
├── secrets.yaml (use external secret management)
├── rbac.yaml
├── worker-deployment.yaml
├── hpa.yaml
├── api-deployment.yaml
├── service.yaml
├── ingress.yaml
├── pdb.yaml
└── network-policy.yaml
```

```yaml
# k8s/kustomization.yaml

apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: customer-success

resources:
- namespace.yaml
- configmap.yaml
- rbac.yaml
- worker-deployment.yaml
- hpa.yaml
- api-deployment.yaml
- service.yaml
- ingress.yaml
- pdb.yaml
- network-policy.yaml

commonLabels:
  app: customer-success-fte
  version: v1

configMapGenerator:
- name: app-config
  envs:
  - config/app.env

secretGenerator:
- name: db-credentials
  envs:
  - secrets/db.env
  type: Opaque
```

---

## Deployment Commands

```bash
# Deploy to Kubernetes
kubectl apply -k k8s/

# Check deployment status
kubectl get deployments -n customer-success
kubectl get pods -n customer-success
kubectl get hpa -n customer-success

# View logs
kubectl logs -f deployment/worker-deployment -n customer-success

# Scale manually
kubectl scale deployment worker-deployment --replicas=5 -n customer-success

# Rollback
kubectl rollout undo deployment/worker-deployment -n customer-success

# Delete deployment
kubectl delete -k k8s/
```

---

## Acceptance Criteria

- [ ] All manifests apply without errors
- [ ] Workers auto-scale based on CPU/memory
- [ ] Health checks pass for all pods
- [ ] Rolling updates work without downtime
- [ ] Secrets are properly mounted
- [ ] Network policies restrict traffic
- [ ] PDB prevents simultaneous pod disruption
- [ ] Ingress routes traffic correctly
- [ ] Resource limits are enforced
- [ ] Pod anti-affinity spreads workers

## Related Skills

- `kafka-event-processing` - Workers consume from Kafka
- `customer-success-agent` - Agent runs in worker pods
- `channel-integrations` - Webhooks exposed via Ingress
- `postgres-crm-schema` - Database connection from pods

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Documentation](https://kustomize.io/)
- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
