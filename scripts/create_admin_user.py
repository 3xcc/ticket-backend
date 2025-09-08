# Run from repo root: python -m scripts.create_admin_user
import os
import sys
from sqlmodel import Session, select

# Ensure repo root on path if run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.engine import engine
from app.models.admin_user import AdminUser
from app.utils.security import get_password_hash

EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@example.com")
PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "strongpassword")
ROLE = os.getenv("SEED_ADMIN_ROLE", "admin")  # If model uses Enum, adjust accordingly

def main():
    with Session(engine) as session:
        existing = session.exec(select(AdminUser).where(AdminUser.email == EMAIL)).first()
        if existing:
            print("Admin already exists:", existing.id, existing.email)
            return
        user = AdminUser(
            email=EMAIL,
            hashed_password=get_password_hash(PASSWORD),
            role=ROLE,
            token_version=0,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        print("Created admin:", user.id, user.email)

if __name__ == "__main__":
    main()
