import time
from app.models import Usage
from sqlmodel import Session, select, func

def record_usage(session: Session, user_id: int):
    usage = Usage(user_id=user_id, timestamp=int(time.time()), count=1)
    session.add(usage)
    session.commit()

def get_user_usage_total(session: Session, user_id: int, period_start: int = None, period_end: int = None) -> int:
    q = select(func.coalesce(func.sum(Usage.count), 0)).where(Usage.user_id == user_id)
    if period_start:
        q = q.where(Usage.timestamp >= period_start)
    if period_end:
        q = q.where(Usage.timestamp <= period_end)
    total = session.exec(q).one()
    return int(total)
