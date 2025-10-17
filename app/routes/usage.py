from fastapi import APIRouter, Depends, HTTPException, Request, Security
from sqlmodel import Session
from app.schemas import UsageRead
from app.database import get_session
from app.auth import verify_api_key
from app.rate_limit import check_user_rate_limit
from app.services.usage_service import record_usage, get_user_usage_total
from app.security import api_key_header

router = APIRouter()

@router.get("/usage", response_model=UsageRead)
def get_usage(
    request: Request,
    session: Session = Depends(get_session),
    api_key: str | None = Security(api_key_header)
):
    user = verify_api_key(session, api_key)
    if not user:
        raise HTTPException(401, "Invalid or missing API key")
    if not check_user_rate_limit(user.id):
        raise HTTPException(429, "Rate limit exceeded")
    record_usage(session, user.id)
    total = get_user_usage_total(session, user.id)
    return UsageRead(total_requests=total)
