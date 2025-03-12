import csv
import re
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from app.database import engine
from app.models.game import Game

class GameDetailsLoader:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.session = sessionmaker(bind=engine)()

    def parse_date(self, date_str):
        if not date_str or "Отзывов нет" in date_str:
            return None
        try:
            return datetime.strptime(date_str, "%d %b, %Y").date()
        except ValueError:
            print(f"⚠ Ошибка обработки даты: {date_str}")
            return None

    def parse_reviews(self, review_text):
        if not review_text or "Отзывов нет" in review_text:
            return None
        match = re.search(r"(\d+)%", review_text)
        return float(match.group(1)) if match else None

    def parse_genres(self, genres_text):
        return genres_text.strip() if genres_text else None

    def parse_russian_supported(self, value):
        return value.strip().lower() == "да"

    def load(self):
        with open(self.csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                game = self.session.query(Game).filter_by(name=row["title"]).one_or_none()

                if not game:
                    print(f"❌ Игра '{row['title']}' не найдена. Пропускаем...")
                    continue

                game.release_date = self.parse_date(row["release_date"])
                game.rating = self.parse_reviews(row["reviews"])
                game.tags = self.parse_genres(row["genres"])
                game.russian_supported = self.parse_russian_supported(row["russian_supported"])

        self.session.commit()
        print("✅ Данные об играх обновлены")

    def close(self):
        self.session.close()

if __name__ == "__main__":
    loader = GameDetailsLoader("game_details_10k.csv")
    loader.load()
    loader.close()
