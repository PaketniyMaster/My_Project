from sqlalchemy import Column, Integer, String, Float, Date, Boolean, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
from sqlalchemy.dialects.postgresql import TSVECTOR
from app.database import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    link = Column(String, nullable=True)
    release_date = Column(Date, nullable=True)
    tags = Column(String, nullable=True)
    russian_supported = Column(Boolean, nullable=True)  
    rating = Column(Float, nullable=True)
    description_ru = Column(String, nullable=True)  # Описание на русском
    description_en = Column(String, nullable=True)  # Описание на английском
    
    # Поле для полнотекстового индекса
    search_vector = Column(TSVECTOR)

    # Это дополнительное поле для полнотекстового поиска
    @validates('description_ru', 'description_en')
    def update_search_vector(self, key, value):
        # Пересчитываем search_vector каждый раз, когда изменяется описание
        if key == 'description_ru' or key == 'description_en':
            # Заменяем None на пустую строку
            description_ru = self.description_ru if self.description_ru else ''
            description_en = self.description_en if self.description_en else ''
            # Объединяем описания для индекса полнотекстового поиска
            self.search_vector = func.to_tsvector('russian', description_ru + ' ' + description_en)
        return value
