from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

class UserRole(str, Enum):
    ADMIN = "admin"
    SUBADMIN = "subadmin"
    EDITOR = "editor"
    SCANNER = "scanner"

class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.SCANNER)
    token_version: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: Optional[bool] = Field(default=True)
