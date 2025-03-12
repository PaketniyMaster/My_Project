import csv
import re
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from app.database import engine
from app.models.game import Game
from app.models.review import Review

class ReviewsLoader:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.session = sessionmaker(bind=engine)()

    def clean_review(self, text):
        patterns_to_remove = [
            r"Пользовател[ейь]?.*посчитал[и]?.*обзор полезным.*",
            r"Ещё никто не посчитал этот обзор полезным.*",
            r"Пользователей, посчитавших обзор полезным: \d+",
            r"Пользователей, посчитавших обзор забавным: \d+",
            r".*пользовател[ейь]?.*посчитал[и]? этот обзор полезным.*",
            r".*пользовател[ейь]?.*посчитал[и]? этот обзор забавным.*",
            r"^\d+\s+.*",
            r"\d+ ч. всего.*",
            r"Опубликовано:.*",
            r"ОБЗОР ПРОДУКТА В РАННЕМ ДОСТУПЕ.*",
            r"На этот обзор есть ответ от разработчика.*",
            r"Товар получен бесплатно",
            r"Have requested a refund\.",
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)

        text = re.sub(r"^\d+\.\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\d+\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"\n\s*\n", "\n", text).strip()

        return text

    def extract_rating(self, text):
        if "Рекомендую" in text:
            return 1
        if "Не рекомендую" in text:
            return 0
        return None

    def process_review_text(self, text):
        return re.sub(r"^(Рекомендую|Не рекомендую)\s*", "", text, flags=re.MULTILINE).strip()

    def load(self):
        with open(self.csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    game = self.session.query(Game).filter_by(name=row["game_title"]).one()
                except NoResultFound:
                    print(f"❌ Игра '{row['game_title']}' не найдена. Пропускаем...")
                    continue

                original_text = row["review_text"]
                rating = self.extract_rating(original_text)
                review_text = self.clean_review(original_text)
                review_text = self.process_review_text(review_text)

                if review_text:
                    review = Review(game_id=game.id, review_text=review_text, rating=rating)
                    self.session.add(review)

        self.session.commit()
        print("✅ Отзывы загружены в БД")

    def close(self):
        self.session.close()

if __name__ == "__main__":
    loader = ReviewsLoader("reviews.csv")
    loader.load()
    loader.close()
