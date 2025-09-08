from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum

class AdminRole(str, Enum):
    ADMIN = "admin"
    SUBADMIN = "subadmin"
    EDITOR = "editor"
    SCANNER = "scanner"

class AdminUser(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    role: AdminRole = Field(default=AdminRole.SCANNER)
    token_version: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime | None = None
