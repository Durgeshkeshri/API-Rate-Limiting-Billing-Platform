from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    username: str
    email: EmailStr

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    active: bool
    model_config = ConfigDict(from_attributes=True)

class APIKeyRead(BaseModel):
    id: int
    prefix: str
    active: bool
    model_config = ConfigDict(from_attributes=True)

class UsageRead(BaseModel):
    total_requests: int

class BillingResponse(BaseModel):
    usage: int
    amount_due: float
    period_start: int
    period_end: int
    model_config = ConfigDict(from_attributes=True)
