from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.game import Game
from app.models.game_descriptions import GameDescription
from app.models.game_summary import GameSummary
from app.services.game import get_game_image_url

router = APIRouter()

@router.get("/games/{id}")
async def get_game(id: int, lang: str = "en", db: Session = Depends(get_db)):
    game_obj = db.query(Game).filter(Game.id == id).first()
    if not game_obj:
        raise HTTPException(status_code=404, detail="Игра не найдена")

    description_obj = db.query(GameDescription).filter(
        GameDescription.game_id == game_obj.id,
        GameDescription.language == lang
    ).first()
    description = description_obj.description if description_obj else ""

    summary_obj = db.query(GameSummary).filter(
        GameSummary.game_id == game_obj.id,
        GameSummary.language == lang
    ).first()
    summary = summary_obj.summary if summary_obj else ""

    return {
        "id": game_obj.id,
        "name": game_obj.name,
        "link": game_obj.link,
        "release_date": game_obj.release_date,
        "tags": game_obj.tags.split(", ") if game_obj.tags else [],
        "russian_supported": game_obj.russian_supported,
        "rating": game_obj.rating,
        "image_url": get_game_image_url(game_obj.link),
        "description": description,
        "summary": summary
    }
