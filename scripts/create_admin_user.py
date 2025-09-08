import sys, os
from datetime import datetime
from sqlmodel import Session, SQLModel
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add repo root to sys.path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import models and engine
from app.db.engine import engine
from app.models.admin_user import AdminUser, AdminRole
from app.utils.security import hash_password

# Create tables if they don't exist
SQLModel.metadata.create_all(engine)

def create_admin(email: str, password: str, role: AdminRole = AdminRole.ADMIN):
    hashed_pw = hash_password(password)
    user = AdminUser(
        email=email,
        hashed_password=hashed_pw,
        role=role,
        token_version=1,
        created_at=datetime.utcnow(),
        last_login=None
    )
    with Session(engine) as session:
        session.add(user)
        session.commit()
        print(f"✅ Created admin user: {email} with role: {role}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_admin_user.py <email> <password> [role]")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    role = AdminRole(sys.argv[3]) if len(sys.argv) > 3 else AdminRole.ADMIN
    create_admin(email, password, role)
