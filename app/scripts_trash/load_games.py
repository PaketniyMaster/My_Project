import csv
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.game import Game

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

CSV_GAMES = "games.csv"

def load_games():
    with open(CSV_GAMES, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            existing_game = session.query(Game).filter_by(name=row["name"]).first()
            if existing_game:
                print(f"⚠ Игра '{row['name']}' уже есть в БД, пропускаем.")
                continue  # Пропускаем запись, если она уже есть

            game = Game(name=row["name"], link=row["link"])
            session.add(game)

    session.commit()
    print("✅ Игры загружены в БД")

load_games()
session.close()
