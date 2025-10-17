Project Summary
---------------

 - Purpose: Issue API keys, enforce per-user rate limits, persist usage in Postgres, and compute usage-based billing
- Auth: `X-API-Key`
- Core stack: FastAPI, SQLModel/Postgres, Redis, Docker, Nginx 
- Docs & health: `/docs`, `/health`

Quick Start (Local)
-------------------

```
docker-compose up --build
```
- API: `http://localhost:8001`
- Docs: `http://localhost:8001/docs`
- Health: `http://localhost:8001/health`

Key Endpoints
-------------

- `POST /users/` → returns one-time `api_key`
- `GET /me` → user info (requires `X-API-Key`)
- `GET /usage` → `{ total_requests }` (rate limited per user)
- `GET /billing` → `{ usage, amount_due, period_start, period_end }`

Config (env)
------------

- `DATABASE_URL`, `REDIS_URL`
- `API_RATE_LIMIT`, `API_RATE_WINDOW`
- `BILLING_UNIT_PRICE`
- `INIT_DB=true|false`

# FastAPI Docker GCP Deployment Guide


## 1. Set Your Active Project and Enable APIs

```

gcloud config set project api-rate-limit-billing-475412
gcloud services enable run.googleapis.com artifactregistry.googleapis.com sqladmin.googleapis.com redis.googleapis.com vpcaccess.googleapis.com

```

---

## 2. Create Cloud SQL (Postgres) Database

```

gcloud sql instances create api-rate-limit-postgres \
--database-version=POSTGRES_14 \
--tier=db-f1-micro \
--region=us-central1

```

```

gcloud sql users create dbuser --instance=api-rate-limit-postgres --password="Durgesh1027"

# Or, if user already exists:

gcloud sql users set-password dbuser --instance=api-rate-limit-postgres --password="Durgesh1027"

```

```

gcloud sql databases create apidb --instance=api-rate-limit-postgres

```

```

gcloud sql instances describe api-rate-limit-postgres --format="value(ipAddresses.ipAddress)"

```
*(Save this IP as `<SQL_IP>`)*

---

## 3. Create Redis (MemoryStore) Instance

```

gcloud redis instances create api-rate-limit-redis \
--size=1 --region=us-central1 --tier=basic

```

```

gcloud redis instances describe api-rate-limit-redis --region=us-central1 --format="value(host)"

```
*(Save this IP as `<REDIS_IP>`)*

---

## 4. Create Serverless VPC Connector

```

gcloud compute networks vpc-access connectors create api-vpc-connector \
--region=us-central1 \
--network=default \
--range=10.8.0.0/28

```

---

## 5. Create Artifact Registry and Docker Auth

```

gcloud artifacts repositories create app-images \
--repository-format=docker \
--location=us-central1 \
--description="Docker images for API Rate Limit Billing Project"

```

```

gcloud auth configure-docker us-central1-docker.pkg.dev

```

---

## 6. Build and Push Docker Image

```

docker build -t us-central1-docker.pkg.dev/api-rate-limit-billing-475412/app-images/api-rate-limit-billing:latest .
docker push us-central1-docker.pkg.dev/api-rate-limit-billing-475412/app-images/api-rate-limit-billing:latest

```

---

## 7. Deploy to Cloud Run

**Replace `<SQL_IP>` and `<REDIS_IP>` with your real values.**

```

gcloud run deploy api-rate-limit-billing --image us-central1-docker.pkg.dev/api-rate-limit-billing-475412/app-images/api-rate-limit-billing:latest --region us-central1 --platform managed --port 8000 --allow-unauthenticated --cpu 1 --memory 1Gi --max-instances 2 --vpc-connector=api-vpc-connector --vpc-egress=all --set-env-vars DATABASE_URL=postgresql+psycopg2://dbuser:Durgesh1027@<SQL_IP>:5432/apidb,REDIS_URL=redis://<REDIS_IP>:6379/0,API_RATE_LIMIT=1000,API_RATE_WINDOW=86400,BILLING_UNIT_PRICE=0.01

```

---

## 8. Get Service URL

```

gcloud run services describe api-rate-limit-billing --region us-central1 --format="value(status.url)"

```
Go to `https://<SERVICE_URL>/health` to verify.

---