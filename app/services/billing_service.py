from app.config import settings
from app.models import Billing
from sqlmodel import Session
from app.services.usage_service import get_user_usage_total

def calculate_billing(session: Session, user_id: int, period_start: int, period_end: int):
    usage = get_user_usage_total(session, user_id, period_start, period_end)
    amount_due = usage * settings.BILLING_UNIT_PRICE
    billing = Billing(
        user_id=user_id,
        usage=usage,
        amount_due=amount_due,
        period_start=period_start,
        period_end=period_end
    )
    session.add(billing)
    session.commit()
    session.refresh(billing)
    return billing
