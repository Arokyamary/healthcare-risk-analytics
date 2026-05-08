from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import User
from app.core.security import get_password_hash

DB_URL = "postgresql://postgres:postgres@127.0.0.1:5432/healthcare_db"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
db = Session()

admin = User(
    email="admin@healthcare.com",
    hashed_password=get_password_hash("admin123"),
    full_name="Admin User",
    role="admin",
    is_active=True
)
db.add(admin)
db.commit()
print("Admin user created: admin@healthcare.com / admin123")