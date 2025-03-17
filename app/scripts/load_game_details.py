import csv
import re
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert
from app.database import engine
from app.models.review import Review
import time

SessionLocal = sessionmaker(bind=engine)

CSV_FILE = "reviews_10k.csv"

class ReviewLoader:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.session = SessionLocal()

    def parse_date(self, date_str):
        if not date_str or "Отзывов нет" in date_str or date_str == "Не указана":
            return None
        try:
            return datetime.strptime(date_str, "%d %b, %Y").date()
        except ValueError:
            return None

    def parse_review_score(self, review_text):
        if not review_text or "Отзывов нет" in review_text:
            return None
        match = re.search(r"(\d+)%", review_text)
        return float(match.group(1)) if match else None

    def load(self):
        try:
            print(f"📥 Начинаем обработку файла: {self.csv_file}")
            start_time = time.time()

            reviews_dict = {}
            with open(self.csv_file, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                for i, row in enumerate(reader, start=1):
                    game_name = row["title"].strip()

                    review_data = {
                        "game_name": game_name,
                        "review_date": self.parse_date(row["review_date"]),
                        "review_score": self.parse_review_score(row["review_score"]),
                        "review_text": row["review_text"].strip() if row["review_text"] else None,
                    }
                    reviews_dict[(game_name, row["review_date"])] = review_data

                    if i % 1000 == 0:
                        print(f"🔄 Обработано {i} строк...")

            reviews_to_update = list(reviews_dict.values())
            print(f"📊 Подготовлено к обновлению: {len(reviews_to_update)} записей")

            if reviews_to_update:
                chunk_size = 1000
                for i in range(0, len(reviews_to_update), chunk_size):
                    chunk = reviews_to_update[i:i + chunk_size]
                    print(f"📦 Обновляем {i + 1}-{i + len(chunk)}...")

                    insert_stmt = insert(Review).values(chunk).on_conflict_do_update(
                        index_elements=["game_name", "review_date"],
                        set_={
                            "review_score": insert(Review).excluded.review_score,
                            "review_text": insert(Review).excluded.review_text,
                        },
                    )
                    self.session.execute(insert_stmt)
                    self.session.commit()

            print(f"✅ Данные успешно обновлены за {time.time() - start_time:.2f} сек")

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.session.rollback()
        finally:
            self.session.close()
            print("🔒 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    loader = ReviewLoader(CSV_FILE)
    loader.load()
