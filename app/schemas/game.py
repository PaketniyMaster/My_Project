from pydantic import BaseModel
from datetime import date
from typing import Optional

class GameResponse(BaseModel):
    name: str
    game_id: int
    image_url: str
    release_date: Optional[date]
    tags: Optional[list[str]]
    russian_supported: bool
    rating: Optional[float]

    class Config:
        from_attributes = True
