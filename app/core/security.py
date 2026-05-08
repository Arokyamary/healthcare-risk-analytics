from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_hours: int = 8) -> str:
    expire = datetime.utcnow() + timedelta(hours=expires_hours)
    payload = {**data, 'exp': expire, 'iat': datetime.utcnow()}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])