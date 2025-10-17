from fastapi import APIRouter, Depends, HTTPException, Request, Security
from sqlmodel import Session
from app.schemas import BillingResponse
from app.database import get_session
from app.auth import verify_api_key
from app.services.billing_service import calculate_billing
from app.security import api_key_header
import time

router = APIRouter()

@router.get("/billing", response_model=BillingResponse)
def get_billing(
    request: Request,
    session: Session = Depends(get_session),
    api_key: str | None = Security(api_key_header)
):
    user = verify_api_key(session, api_key)
    if not user:
        raise HTTPException(401, "Invalid or missing API key")
    now = int(time.time())
    period_start = now - (24 * 3600)  # last 24 hours
    period_end = now
    billing = calculate_billing(session, user.id, period_start, period_end)
    return BillingResponse.model_validate(billing)
