import csv
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from app.database import engine
from app.models.game import Game
from app.models.review import Review

BATCH_SIZE = 100  # размер пакета, можно изменить
MAX_WORKERS = 5   # число потоков для каждого пакета

class ReviewsLoader:
    def __init__(self, csv_file, max_workers=MAX_WORKERS, batch_size=BATCH_SIZE):
        self.csv_file = csv_file
        self.max_workers = max_workers
        self.batch_size = batch_size

    def clean_review(self, text):
        """Удаляет ненужные элементы из отзыва."""
        patterns_to_remove = [
            r"\[/?h1\]", r"\[/?b\]", r"\[/?i\]", r"\[/?list\]", r"\[\*\]", r"\[/?h2\]",
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
        text = re.sub(r"\n\s*\n", "\n", text).strip()  # Убираем лишние переносы строк
        return text

    def extract_rating(self, review_type):
        """Конвертирует 'Положительный' -> 1, 'Отрицательный' -> 0"""
        if "Положительный" in review_type:
            return 1
        if "Отрицательный" in review_type:
            return 0
        return None

    def process_row(self, row):
        """Обрабатывает одну строку CSV в отдельном потоке."""
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        try:
            # Поиск игры по названию
            try:
                game = session.query(Game).filter_by(name=row["game_title"]).one()
            except NoResultFound:
                print(f"❌ Игра '{row['game_title']}' не найдена. Пропускаем...")
                return

            original_text = row["review_text"]
            rating = self.extract_rating(row["review_type"])
            review_text = self.clean_review(original_text)

            if review_text:  # Пропускаем пустые отзывы
                review = Review(game_id=game.id, review_text=review_text, rating=rating)
                session.add(review)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Ошибка при обработке отзыва для игры '{row['game_title']}': {e}")
        finally:
            session.close()

    def process_batch(self, batch):
        """Обрабатывает пакет строк параллельно."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.process_row, row) for row in batch]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print("Ошибка в будущем:", e)

    def load(self):
        """Обрабатывает CSV пакетами и загружает отзывы в БД."""
        batch = []
        with open(self.csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                batch.append(row)
                if len(batch) >= self.batch_size:
                    self.process_batch(batch)
                    print(f"✅ Обработан пакет из {len(batch)} строк")
                    batch = []
            if batch:
                self.process_batch(batch)
                print(f"✅ Обработан последний пакет из {len(batch)} строк")

        print("✅ Отзывы загружены в БД")

if __name__ == "__main__":
    loader = ReviewsLoader(r"D:\VSC Projects\App\Project\app\csv\reviews_10K-15k.csv")
    loader.load()
