from sqlalchemy import create_engine, text
from app.db.models import Base
from app.core.security import get_password_hash
from app.db.models import User
from sqlalchemy.orm import sessionmaker

RAILWAY_URL = "postgresql://postgres:uykweXXcynlmeYaXItiNbmbGcWxDlLMg@turntable.proxy.rlwy.net:19990/railway"

engine = create_engine(RAILWAY_URL)

# Enable extensions FIRST
print("Enabling extensions...")
with engine.connect() as conn:
    conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
    conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))
    conn.commit()
print("Extensions enabled!")

# Then create tables
print("Creating tables on Railway...")
Base.metadata.create_all(engine)
print("Tables created!")

# Load admin user
Session = sessionmaker(bind=engine)
db = Session()

existing = db.query(User).filter(User.email == "admin@healthcare.com").first()
if not existing:
    admin = User(
        email="admin@healthcare.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User",
        role="admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    print("Admin user created!")
else:
    print("Admin user already exists!")

print("Railway setup complete!")