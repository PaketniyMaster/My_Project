from pydantic import BaseModel
from datetime import date
from typing import Optional

class GameResponse(BaseModel):
    name: str
    image_url: str
    release_date: Optional[date]
    tags: Optional[str]
    russian_supported: bool
    rating: Optional[float]

    class Config:
        from_attributes = True
