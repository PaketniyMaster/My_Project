from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.game import GameResponse
from app.crud.game import search_games
from app.services.game import get_game_image_url, extract_game_id
from fastapi.security import OAuth2PasswordBearer
from app.models.game import Game
from app.models.game_descriptions import GameDescription
from sqlalchemy import func


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

@router.get("/games/search_by_language", response_model=list[GameResponse])
def search_games_by_language_endpoint(
    query: str,
    language: str = "english",  # Допустим, по умолчанию язык будет английский
    tags: str = None,
    min_rating: float = None,
    max_rating: float = None,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    tags_list = tags.split(",") if tags else []
    # Добавляем логику для фильтрации по языку
    games = search_games_by_language(db, query, language, tags_list, min_rating, max_rating)
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

# Функция для поиска с учётом языка
def search_games_by_language(db: Session, query: str, language: str, tags: list, min_rating: float, max_rating: float):
    # Формируем строку для tsquery, экранируя пробелы
    query = query.replace(" ", " & ")

    # Определяем нужную колонку для поиска в зависимости от языка
    search_column = 'description_ru' if language == 'ru' else 'description_en'

    # Строим запрос с учетом языка
    query = db.query(Game).join(GameDescription).filter(
        GameDescription.search_vector.op('@@')(func.to_tsquery(language, query))
    )
    
    # Фильтрация по тегам, рейтингам и другим параметрам
    if tags:
        query = query.filter(Game.tags.op('=')(tags))  # Поиск по тегам
    
    if min_rating:
        query = query.filter(Game.rating >= min_rating)
    
    if max_rating:
        query = query.filter(Game.rating <= max_rating)
    
    return query.all()

