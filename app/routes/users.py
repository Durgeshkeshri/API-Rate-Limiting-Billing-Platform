from fastapi import APIRouter, Depends, HTTPException, Request, Security
from sqlmodel import Session, select
from app.schemas import UserCreate, UserRead
from app.models import User, APIKey
from app.database import get_session
from app.auth import generate_api_key, verify_api_key
from app.security import api_key_header
from app.services.usage_service import record_usage

router = APIRouter()

@router.post("/users/", response_model=dict)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
	if session.exec(select(User).where(User.username == user.username)).first():
		raise HTTPException(400, "Username already exists")
	if session.exec(select(User).where(User.email == user.email)).first():
		raise HTTPException(400, "Email already registered")
	obj = User(**user.model_dump(), active=True)
	session.add(obj)
	session.commit()
	session.refresh(obj)
	api_key, hash_, prefix = generate_api_key()
	key = APIKey(user_id=obj.id, key_hash=hash_, prefix=prefix, active=True)
	session.add(key)
	session.commit()
	session.refresh(key)
	return {
		"user": UserRead.model_validate(obj),
		"api_key": api_key,
		"prefix": key.prefix,
		"message": "Save your API key. It is shown once only!"
	}

@router.get("/me", response_model=UserRead)
def get_me(
	request: Request,
	session: Session = Depends(get_session),
	api_key: str | None = Security(api_key_header)
):
	user = verify_api_key(session, api_key)
	if not user:
		raise HTTPException(401, "Invalid or missing API key")
	# Track usage of the /me endpoint
	record_usage(session, user.id)
	return UserRead.model_validate(user)
