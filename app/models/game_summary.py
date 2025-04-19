from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class GameSummary(Base):
    __tablename__ = "game_summary"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    summary = Column(String, nullable=False)
    language = Column(String, default="ru")  # "ru" или "en"
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
