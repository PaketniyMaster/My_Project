from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from app.database import Base

class GameDescription(Base):
    __tablename__ = "game_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    language = Column(String, nullable=False)  # 'ru' или 'en'
    description = Column(String, nullable=True)

    search_vector = Column(TSVECTOR)

    game = relationship("Game", back_populates="descriptions")

    @validates("description")
    def update_search_vector(self, key, value):
        safe_value = value or ""
        lang = (self.language or "").lower()
        if lang == "ru":
            self.search_vector = func.to_tsvector("russian", safe_value)
        else:
            self.search_vector = func.to_tsvector("english", safe_value)
        return value
