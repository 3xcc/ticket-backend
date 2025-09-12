from sqlmodel import Session
from app.db.engine import engine
from app.models.user import User, UserRole
from app.utils.auth import hash_password

with Session(engine) as session:
    legacy_id = "1"
    existing = session.get(User, legacy_id)
    if not existing:
        user = User(
            id=legacy_id,
            email="legacy_1@scanner.com",
            hashed_password=hash_password("placeholder"),
            role=UserRole.SCANNER,
            token_version=1,
            is_active=True
        )
        session.add(user)
        session.commit()
        print("✅ Seeded legacy user with ID 1")
    else:
        print("⚠️ User with ID 1 already exists")
