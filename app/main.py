import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.routes.users import router as users_router
from app.routes.usage import router as usage_router
from app.routes.billing import router as billing_router
from app.routes.health import router as health_router
from app.database import init_db

app = FastAPI(
    title="API Rate Limiting & Billing Platform",
    description="Scalable backend for usage monitoring, limiting and billing."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.on_event("startup")
def on_startup():
    if os.getenv("INIT_DB", "true").lower() == "true":
        init_db()

app.include_router(health_router)
app.include_router(users_router)
app.include_router(usage_router)
app.include_router(billing_router)

# Customize OpenAPI to include ApiKeyAuth and apply it to protected routes
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version="0.1.0",
        description=app.description,
        routes=app.routes,
    )
    # Apply security to specific operations
    paths = openapi_schema.get("paths", {})
    for p in ["/usage", "/billing", "/me"]:
        if p in paths and "get" in paths[p]:
            paths[p]["get"]["security"] = [{"APIKeyHeader": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
