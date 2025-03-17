from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.game import GameResponse
from app.crud.game import search_games
from app.services.game import get_game_image_url

router = APIRouter()

@router.get("/games/search", response_model=list[GameResponse])
def search_games_endpoint(query: str, db: Session = Depends(get_db)):
    games = search_games(db, query)
    return [
        GameResponse(
            name=game.name,
            image_url=get_game_image_url(game.link),
            release_date=game.release_date,
            tags=game.tags,
            russian_supported=bool(game.russian_supported),
            rating=game.rating
        ) for game in games
    ]

@router.options("/games/search")
async def options_handler():
    return {}