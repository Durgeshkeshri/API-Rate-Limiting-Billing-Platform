# API Rate Limiting & Billing Platform

A scalable backend platform for API usage monitoring, rate limiting, and billing with support for Docker, Kubernetes, and Google Cloud Platform deployments.

## 📋 Project Summary

- **Purpose**: Issue API keys, enforce per-user rate limits, persist usage in Postgres, and compute usage-based billing
- **Auth**: `X-API-Key` header-based authentication
- **Core Stack**: FastAPI, SQLModel/Postgres, Redis, Docker, Nginx, Kubernetes
- **Documentation**: Available at `/docs` (Swagger UI)
- **Health Check**: Available at `/health`

## 🚀 Key Features

- ✅ User registration with automatic API key generation
- ✅ Per-user rate limiting using Redis
- ✅ Usage tracking and billing calculation
- ✅ Horizontal scaling with Kubernetes
- ✅ High availability with multiple replicas
- ✅ Auto-scaling based on CPU/Memory usage
- ✅ Load balancing with Nginx

## 🔑 Key Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/users/` | POST | No | Create user and get one-time API key |
| `/me` | GET | Yes | Get current user info |
| `/usage` | GET | Yes | Get total request count (rate limited) |
| `/billing` | GET | Yes | Get billing info for last 24 hours |
| `/health` | GET | No | Health check for all services |

---

## 🏠 Local Development Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed
- [Git](https://git-scm.com/downloads) installed

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/api-rate-limit-billing.git
cd api-rate-limit-billing
```

### 2. Environment Configuration

Create a `.env` file in the project root (or use the existing one):

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/apidb
REDIS_URL=redis://localhost:6379/0
API_RATE_LIMIT=1000
API_RATE_WINDOW=86400
BILLING_UNIT_PRICE=0.01
```

### 3. Start with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

**Services will be available at:**
- **API**: `http://localhost:8001`
- **API Docs**: `http://localhost:8001/docs`
- **Health Check**: `http://localhost:8001/health`
- **Nginx Load Balancer**: `http://localhost:80`
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`

### 4. Test the Application

```bash
# Check health
curl http://localhost:8001/health

# Create a user
curl -X POST http://localhost:8001/users/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com"}'

# Save the API key from response, then test
export API_KEY="sk_your_api_key_here"

# Get user info
curl http://localhost:8001/me -H "X-API-Key: $API_KEY"

# Get usage
curl http://localhost:8001/usage -H "X-API-Key: $API_KEY"

# Get billing
curl http://localhost:8001/billing -H "X-API-Key: $API_KEY"
```

### 5. Stop Services

```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers with volumes (clean database)
docker-compose down -v
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

- [Docker Desktop with Kubernetes enabled](https://docs.docker.com/desktop/kubernetes/)
-  [kubectl](https://kubernetes.io/docs/tasks/tools/) installed and configured
- Docker image built and available locally or pushed to a registry (Docker Hub)

### 1. Build and Push Docker Image

```bash
# Build the image
docker build -t durgeshkeshri/api-rate-limit-billing:latest .

# Push to Docker Hub (or your registry)
docker push durgeshkeshri/api-rate-limit-billing:latest
```

### 2. Deploy to Kubernetes

```bash
# Apply all Kubernetes resources
kubectl apply -f kubernetes.yaml
```

This creates:
- **Namespace**: `api-billing-platform`
- **PostgreSQL StatefulSet**: 1 pod with persistent storage (10GB)
- **Redis Deployment**: 1 pod for rate limiting
- **API Deployment**: 3 pods (auto-scales 3-10)
- **Nginx Deployment**: 2 pods for load balancing
- **Services**: ClusterIP and LoadBalancer
- **HPA**: Horizontal Pod Autoscaler
- **PDB**: Pod Disruption Budget for high availability

### 3. Monitor Deployment

```bash
# Check all pods
kubectl get pods -n api-billing-platform

# Watch pods until all are Running
kubectl get pods -n api-billing-platform -w

# Check all resources
kubectl get all -n api-billing-platform

# View logs
kubectl logs -f deployment/api -n api-billing-platform
```

### 4. Get Application URL

```bash
# Get the external IP (may take 1-2 minutes)
kubectl get svc nginx-service -n api-billing-platform
# Access via: http://localhost:8080
```

```

### 6. Kubernetes Management Commands

```bash
# Scale API pods manually
kubectl scale deployment api --replicas=5 -n api-billing-platform

# Check auto-scaling status
kubectl get hpa -n api-billing-platform

# View detailed pod info
kubectl describe pod <pod-name> -n api-billing-platform

# Execute commands in a pod
kubectl exec -it deployment/api -n api-billing-platform -- /bin/bash

# View all logs
kubectl logs -f -l app=api -n api-billing-platform

# Restart deployment (rolling update)
kubectl rollout restart deployment/api -n api-billing-platform

# Check rollout status
kubectl rollout status deployment/api -n api-billing-platform

# View events
kubectl get events -n api-billing-platform --sort-by='.lastTimestamp'
```

### 7. Cleanup Kubernetes Resources

```bash
# Delete all resources
kubectl delete -f kubernetes.yaml

# Verify deletion
kubectl get all -n api-billing-platform
```

---

## ☁️ Google Cloud Platform Deployment

### 1. Set Your Active Project and Enable APIs

```bash
gcloud config set project api-rate-limit-billing-475412
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  vpcaccess.googleapis.com
```

### 2. Create Cloud SQL (Postgres) Database

```bash
# Create instance
gcloud sql instances create api-rate-limit-postgres \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1

# Create user
gcloud sql users create dbuser \
  --instance=api-rate-limit-postgres \
  --password="Durgesh1027"

# Create database
gcloud sql databases create apidb \
  --instance=api-rate-limit-postgres

# Get SQL IP address
gcloud sql instances describe api-rate-limit-postgres \
  --format="value(ipAddresses.ipAddress)"
```
*Save this IP as `<SQL_IP>`*

### 3. Create Redis (MemoryStore) Instance

```bash
# Create Redis instance
gcloud redis instances create api-rate-limit-redis \
  --size=1 \
  --region=us-central1 \
  --tier=basic

# Get Redis IP address
gcloud redis instances describe api-rate-limit-redis \
  --region=us-central1 \
  --format="value(host)"
```
*Save this IP as `<REDIS_IP>`*

### 4. Create Serverless VPC Connector

```bash
gcloud compute networks vpc-access connectors create api-vpc-connector \
  --region=us-central1 \
  --network=default \
  --range=10.8.0.0/28
```

### 5. Create Artifact Registry and Configure Docker

```bash
# Create repository
gcloud artifacts repositories create app-images \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker images for API Rate Limit Billing Project"

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev
```

### 6. Build and Push Docker Image

```bash
# Build image
docker build -t us-central1-docker.pkg.dev/api-rate-limit-billing-475412/app-images/api-rate-limit-billing:latest .

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/api-rate-limit-billing-475412/app-images/api-rate-limit-billing:latest
```

### 7. Deploy to Cloud Run

**Replace `<SQL_IP>` and `<REDIS_IP>` with your actual values:**

```bash
gcloud run deploy api-rate-limit-billing \
  --image us-central1-docker.pkg.dev/api-rate-limit-billing-475412/app-images/api-rate-limit-billing:latest \
  --region us-central1 \
  --platform managed \
  --port 8000 \
  --allow-unauthenticated \
  --cpu 1 \
  --memory 1Gi \
  --max-instances 2 \
  --vpc-connector=api-vpc-connector \
  --vpc-egress=all \
  --set-env-vars DATABASE_URL=postgresql+psycopg2://dbuser:Durgesh1027@<SQL_IP>:5432/apidb,REDIS_URL=redis://<REDIS_IP>:6379/0,API_RATE_LIMIT=1000,API_RATE_WINDOW=86400,BILLING_UNIT_PRICE=0.01
```

### 8. Get Service URL

```bash
gcloud run services describe api-rate-limit-billing \
  --region us-central1 \
  --format="value(status.url)"
```

Visit `https://<SERVICE_URL>/health` to verify deployment.

---

## 📊 Load Testing

A comprehensive load test script is included to test your deployment.

### Run Load Test

```bash
# Install dependencies
pip install requests

# Run with default settings (100 users, 10000 requests)
python tests/test_rate_limit.py

# Custom settings
export API_BASE=http://localhost:8001
export LT_USERS=50
export LT_REQUESTS=5000
export LT_CONCURRENCY=50
python tests/test_rate_limit.py
```

### Load Test Environment Variables

- `API_BASE`: Base URL of your API (default: `http://localhost:8001`)
- `LT_USERS`: Number of users to create (default: `100`)
- `LT_REQUESTS`: Total requests to send (default: `10000`)
- `LT_CONCURRENCY`: Concurrent requests (default: `100`)
- `LT_ENDPOINT`: Target endpoint (default: `/usage`)

---

## 🏗️ Architecture Overview

### Docker Compose (Local Development)
- **2 API instances** (api1, api2) on ports 8001, 8002
- **1 PostgreSQL** instance on port 5432
- **1 Redis** instance on port 6379
- **1 Nginx** load balancer on port 80

### Kubernetes (Production)
- **3-10 API pods** (auto-scaling based on CPU/memory)
- **1 PostgreSQL StatefulSet** with 10GB persistent volume
- **1 Redis pod** for distributed rate limiting
- **2 Nginx pods** for high availability
- **LoadBalancer service** for external access
- **Horizontal Pod Autoscaler** for automatic scaling
- **Pod Disruption Budget** to ensure minimum availability

### Key Components

| Component | Purpose | Replicas | Shared/Individual |
|-----------|---------|----------|-------------------|
| PostgreSQL | Persistent data storage | 1 | Shared by all API pods |
| Redis | Rate limiting cache | 1 | Shared by all API pods |
| API Pods | FastAPI application | 3-10 | Independent, stateless |
| Nginx Pods | Load balancing & reverse proxy | 2 | Independent |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | PostgreSQL connection string |
| `REDIS_URL` | - | Redis connection string |
| `API_RATE_LIMIT` | 1000 | Requests per window |
| `API_RATE_WINDOW` | 86400 | Time window in seconds (24h) |
| `BILLING_UNIT_PRICE` | 0.01 | Price per request |
| `INIT_DB` | true | Initialize database tables |
| `DB_POOL_SIZE` | 20 | Database connection pool size |
| `DB_MAX_OVERFLOW` | 40 | Max overflow connections |
| `DB_POOL_TIMEOUT` | 30 | Connection timeout in seconds |
| `DB_POOL_RECYCLE` | 1800 | Recycle connections after seconds |

---

## 📁 Project Structure

```
api-rate-limit-billing/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # SQLModel database models
│   ├── schemas.py           # Pydantic schemas
│   ├── config.py            # Configuration settings
│   ├── auth.py              # API key generation & verification
│   ├── rate_limit.py        # Rate limiting logic
│   ├── redis_client.py      # Redis connection
│   ├── database.py          # Database connection & initialization
│   ├── security.py          # Security utilities
│   ├── routes/
│   │   ├── users.py         # User management endpoints
│   │   ├── usage.py         # Usage tracking endpoints
│   │   ├── billing.py       # Billing endpoints
│   │   └── health.py        # Health check endpoint
│   └── services/
│       ├── usage_service.py # Usage business logic
│       └── billing_service.py # Billing calculations
├── nginx/
│   └── default.conf         # Nginx configuration
├── tests/
│   └── test_rate_limit.py   # Load testing script
├── .env                     # Environment variables
├── docker-compose.yml       # Docker Compose configuration
├── kubernetes.yaml          # Kubernetes deployment
├── Dockerfile              # Docker image definition
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## 🔒 Security Features

- ✅ API key-based authentication
- ✅ SHA-256 hashed API keys in database
- ✅ Rate limiting to prevent abuse
- ✅ Network policies in Kubernetes
- ✅ Resource limits to prevent resource exhaustion
- ✅ Health checks for all services

---

**Built with ❤️ using FastAPI, Kubernetes, and Docker**