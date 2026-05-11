from pydantic import BaseModel, EmailStr


class OperatorResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool

    class Config:
        from_attributes = True