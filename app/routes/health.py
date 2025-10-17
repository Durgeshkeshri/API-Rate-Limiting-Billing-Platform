from fastapi import APIRouter
from app.database import check_db_connection
from app.redis_client import check_redis_connection

router = APIRouter()

@router.get("/health")
def health():
    db_status = "ok" if check_db_connection() else "error"
    redis_status = "ok" if check_redis_connection() else "error"
    return {
        "status": "ok",
        "database": db_status,
        "redis": redis_status
    }
