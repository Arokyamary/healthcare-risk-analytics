from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User
from app.core.security import verify_password, create_access_token, decode_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")
    token = create_access_token(data={'sub': str(user.id), 'role': user.role})
    return {
        'access_token': token, 'token_type': 'bearer',
        'role': user.role, 'name': user.full_name
    }

async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
        user_id = payload.get('sub')
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user