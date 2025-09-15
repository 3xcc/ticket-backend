from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    token_version: Optional[int] = None

    class Config:
        from_attributes = True  # Allows ORM objects to be returned directly
