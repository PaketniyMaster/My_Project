from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import or_, desc
from app.models.game import Game

def search_games(db: Session, query: str, tags: list[str] = None, min_date: str = None, max_date: str = None, min_rating: float = None, max_rating: float = None):
    games_query = db.query(Game).filter(Game.name.ilike(f"%{query}%"))

    if tags:
        tag_filters = [Game.tags.ilike(f"%{tag}%") for tag in tags]
        games_query = games_query.filter(*tag_filters)

    if min_date:
        games_query = games_query.filter(Game.release_date >= min_date)

    if max_date:
        games_query = games_query.filter(Game.release_date <= max_date)

    if min_rating:
        games_query = games_query.filter(Game.rating >= min_rating)

    if max_rating:
        games_query = games_query.filter(Game.rating <= max_rating)

    return games_query.limit(50).all()

def get_game_by_id(db: Session, game_id: str):
    return db.query(Game).filter(Game.id == game_id).first()
