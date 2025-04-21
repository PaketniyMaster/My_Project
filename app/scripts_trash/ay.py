import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.game import Game
from app.models.review import Review

# Указываем строку подключения к базе данных
DATABASE_URL = "postgresql+psycopg2://postgres:Paket12@localhost:5432/GamesAnalysis"  # замените на свою строку подключения

# Настройка подключения к БД
engine = create_engine(DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()

# Список названий игр, для которых нужно выгрузить отзывы
game_titles = [
    "FINAL FANTASY II", "FINAL FANTASY III", "FINAL FANTASY IV", "FINAL FANTASY V", 
    "FINAL FANTASY VII REMAKE INTERGRADE", "CRISIS CORE –FINAL FANTASY VII– REUNION", 
    "STRANGER OF PARADISE FINAL FANTASY ORIGIN", "DARK SOULS™ III", "DARK SOULS™: REMASTERED", 
    "Darksiders Warmastered Edition", "Darksiders III", "Assassin's Creed® Odyssey", 
    "Assassin's Creed Mirage", "Assassin's Creed® III Remastered", "LEGO® MARVEL's Avengers", 
    "The LEGO® NINJAGO® Movie Video Game", "LEGO® DC Super-Villains", "LEGO® Bricktales"
]
  # замените на нужные названия

# Открываем CSV файл для записи
with open(r'D:\VSC Projects\App\Project\app\csv\For_summarize.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['game_title', 'review_type', 'review_text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

    writer.writeheader()

    for game_title_input in game_titles:
        # Ищем игру по названию
        game = session.query(Game).filter(Game.name.ilike(game_title_input)).first()

        if game:
            # Выбираем отзывы для найденной игры
            reviews = session.query(Review).filter(Review.game_id == game.id).all()

            for review in reviews:
                review_type = "Positive" if review.sentiment == "positive" else "Negative" if review.sentiment == "negative" else "Neutral"
                writer.writerow({
                    'game_title': game.name,
                    'review_type': review_type,
                    'review_text': review.review_text
                })
            print(f"Отзывы по игре '{game.name}' успешно выгружены в CSV.")
        else:
            print(f"Игра с названием '{game_title_input}' не найдена.")

# Закрываем сессию
session.close()
