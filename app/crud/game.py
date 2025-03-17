from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.game import Game

def search_games(db: Session, query: str):
    stmt = select(Game).where(Game.name.ilike(f"%{query}%"))
    return db.execute(stmt).scalars().all()
