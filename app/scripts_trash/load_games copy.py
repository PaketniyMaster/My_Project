import csv
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.game import Game

class GamesLoader:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.session = sessionmaker(bind=engine)()

    def load(self):
        with open(self.csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_game = self.session.query(Game).filter_by(name=row["name"]).first()
                if existing_game:
                    print(f"⚠ Игра '{row['name']}' уже есть в БД, пропускаем.")
                    continue  

                game = Game(name=row["name"], link=row["link"])
                self.session.add(game)

        self.session.commit()
        print("✅ Игры загружены в БД")

    def close(self):
        self.session.close()

if __name__ == "__main__":
    loader = GamesLoader("games.csv")
    loader.load()
    loader.close()
