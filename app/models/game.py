from sqlalchemy import Column, Integer, String, Float, Date
from app.database import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    link = Column(String, nullable=True)
    release_date = Column(Date, nullable=True)
    tags = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    positive_percent = Column(Float, nullable=True)
