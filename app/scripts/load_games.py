import csv
from sqlalchemy import exists, func
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.game import Game

SessionLocal = sessionmaker(bind=engine)

CSV_GAMES = r"D:\VSC Projects\App\Project\app\csv\NICE.csv"

def load_games():
    session = SessionLocal()
    try:
        with open(CSV_GAMES, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                game_exists = session.query(
                    exists().where(func.lower(Game.name) == row["name"].lower())
                ).scalar()

                if game_exists:
                    print(f"⚠ Игра '{row['name']}' уже есть в БД, пропускаем.")
                    continue

                game = Game(name=row["name"], link=row["link"])
                session.add(game)
                session.commit()

        print("✅ Игры загружены в БД")
    finally:
        session.close()

load_games()
