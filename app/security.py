from fastapi.security.api_key import APIKeyHeader

# Expose a reusable API key header dependency for Swagger UI (Authorize button)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


