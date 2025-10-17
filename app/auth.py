import hashlib, secrets
from app.models import APIKey, User
from sqlmodel import Session, select

def generate_api_key():
    raw = secrets.token_urlsafe(32)
    api_key = f"sk_{raw}"
    hash_ = hashlib.sha256(api_key.encode()).hexdigest()
    prefix = api_key[:12]
    return api_key, hash_, prefix

def verify_api_key(session: Session, api_key: str):
    if not api_key:
        return None
    hash_ = hashlib.sha256(api_key.encode()).hexdigest()
    key_obj = session.exec(select(APIKey).where(APIKey.key_hash == hash_, APIKey.active == True)).first()
    if not key_obj:
        return None
    user = session.get(User, key_obj.user_id)
    return user if user and user.active else None
