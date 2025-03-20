from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.game import Game
from app.services.game import get_game_image_url

router = APIRouter()

@router.get("/games/{id}")
async def get_game(id: int, db: Session = Depends(get_db)):
    game_obj = db.query(Game).filter(Game.id == id).first()
    if not game_obj:
        raise HTTPException(status_code=404, detail="Игра не найдена")
    
    return {
        "id": game_obj.id,
        "name": game_obj.name,
        "link": game_obj.link,
        "release_date": game_obj.release_date,
        "tags": game_obj.tags.split(", ") if game_obj.tags else [],
        "russian_supported": game_obj.russian_supported,
        "rating": game_obj.rating,
        "image_url": get_game_image_url(game_obj.link)  # Здесь добавляем ссылку на изображение
    }
