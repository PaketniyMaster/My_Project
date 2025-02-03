from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="CASCADE"))
    link = Column(String, nullable=True)  # <-- добавляем ссылку
    review_text = Column(String, nullable=False)
    rating = Column(Integer, nullable=True)
    sentiment = Column(String, nullable=True)
