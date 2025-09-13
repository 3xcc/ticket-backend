from app.db.session import get_session
from app.models.user import User
from app.utils.auth import hash_password
import uuid
from datetime import datetime

def create_admin():
    session = next(get_session())
    try:
        new_user = User(
            id=str(uuid.uuid4()),
            email="admin@example.com",
            hashed_password=hash_password("admin1234"),
            role="admin",
            token_version=1,
            created_at=datetime.utcnow(),
            is_active=True
        )
        session.add(new_user)
        session.commit()
        print(f"✅ Created admin: {new_user.email}")
    finally:
        session.close();

if __name__ == "__main__":
    create_admin()
