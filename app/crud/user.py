from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserCreate
from app.services.auth import get_password_hash

def create_user(db: Session, user_data: UserCreate):
    hashed_password = get_password_hash(user_data.password)
    db_user = User(username=user_data.username, email=user_data.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
