import csv
import locale
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
        locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")

    def parse_date(self, date_str):
        if not date_str or "Отзывов нет" in date_str:
            return None
        try:
            date_str = date_str.replace(" г.", "").strip()
            date_str = re.sub(r"[^a-zA-Zа-яА-Я0-9 ]", " ", date_str)

            month_map = {
                "янв": "01", "фев": "02", "мар": "03", "апр": "04",
                "май": "05", "июн": "06", "июл": "07", "авг": "08",
                "сен": "09", "окт": "10", "ноя": "11", "дек": "12"
            }

            parts = date_str.split()
            if len(parts) != 3:
                raise ValueError("Неправильный формат даты")

            day, month, year = parts
            month = month_map.get(month.lower(), month)
            formatted_date = f"{year}-{month}-{day}"

            return datetime.strptime(formatted_date, "%Y-%m-%d")
        except Exception as e:
            print(f"⚠ Ошибка обработки даты: {date_str} ({e})")
            return None

    def parse_reviews(self, review_text):
        if "Отзывов нет" in review_text:
            return None
        try:
            percent = review_text.split("%")[0]
            return float(percent) if percent.isdigit() else None
        except:
            return None

    def parse_genres(self, genres_text):
        return genres_text.strip() if genres_text else None

    def load(self):
        with open(self.csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    game = self.session.query(Game).filter_by(name=row["title"]).one()
                except NoResultFound:
                    print(f"❌ Игра '{row['title']}' не найдена. Пропускаем...")
                    continue

                game.release_date = self.parse_date(row["release_date"])
                game.positive_percent = self.parse_reviews(row["reviews"])
                game.tags = self.parse_genres(row["genres"])

        self.session.commit()
        print("✅ Данные об играх обновлены")

    def close(self):
        self.session.close()

if __name__ == "__main__":
    loader = GameDetailsLoader("game_details.csv")
    loader.load()
    loader.close()
