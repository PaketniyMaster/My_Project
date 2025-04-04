from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.game import GameResponse
from app.crud.game import search_games
from app.services.game import get_game_image_url, extract_game_id
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

@router.get("/games/search", response_model=list[GameResponse])
def search_games_endpoint(
    query: str,
    tags: str = None,
    min_rating: float = None,
    max_rating: float = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    tags_list = tags.split(",") if tags else []
    games = search_games(db, query, tags_list, min_rating, max_rating)
    return [
        GameResponse(
            name=game.name,
            game_id=game.id,
            image_url=get_game_image_url(game.link),
            release_date=game.release_date,
            tags=game.tags.split(", ") if game.tags else [],
            russian_supported=bool(game.russian_supported),
            rating=game.rating
        ) for game in games
    ]
