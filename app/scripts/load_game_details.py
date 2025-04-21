import csv
import re
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.game import Game
from app.models.game_descriptions import GameDescription
from deep_translator import GoogleTranslator
from tqdm import tqdm  # Импортируем tqdm для прогресс-бара

SessionLocal = sessionmaker(bind=engine)

CSV_FILE = r"D:\VSC Projects\App\Project\app\csv\NICE_details.csv"

class GameDetailsLoader:

    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.session = SessionLocal()

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

    def parse_description(self, description_text):
        return description_text.strip() if description_text else None

    def translate_to_russian(self, text):
        try:
            return GoogleTranslator(source='en', target='ru').translate(text)
        except Exception as e:
            print(f"⚠ Ошибка перевода: {e}")
            return None

    def save_description(self, game_id, language, description):
        if not description:
            return
        # Проверка — если уже есть описание с этим языком, обновим его
        existing = self.session.query(GameDescription).filter_by(game_id=game_id, language=language).first()
        if existing:
            existing.description = description
        else:
            desc = GameDescription(game_id=game_id, language=language, description=description)
            self.session.add(desc)

    def load(self):
        with open(self.csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            total_rows = sum(1 for _ in reader)  # Считаем количество строк для прогресс-бара
            file.seek(0)  # Сбрасываем указатель файла, чтобы снова начать читать

            with tqdm(total=total_rows, desc="Загрузка данных", unit="строка") as pbar:
                count = 0
                for row in reader:
                    game = self.session.query(Game).filter_by(name=row["title"]).one_or_none()
                    if not game:
                        print(f"❌ Игра '{row['title']}' не найдена. Пропускаем...")
                        pbar.update(1)
                        continue

                    game.release_date = self.parse_date(row["release_date"])
                    game.rating = self.parse_reviews(row["reviews"])
                    game.tags = self.parse_genres(row["genres"])
                    game.russian_supported = self.parse_russian_supported(row["russian_supported"])

                    description_en = self.parse_description(row["description"])
                    if description_en:
                        self.save_description(game.id, "en", description_en)

                        translated = self.translate_to_russian(description_en)
                        if translated:
                            self.save_description(game.id, "ru", translated)

                    count += 1
                    pbar.update(1)

                    # Сохраняем данные каждые 100 записей
                    if count % 100 == 0:
                        self.session.commit()

                # После завершения обработки всех строк, делаем финальный commit
                self.session.commit()
        print("✅ Данные об играх и описаниях обновлены")

    def close(self):
        self.session.close()


if __name__ == "__main__":
    loader = GameDetailsLoader(CSV_FILE)
    loader.load()
    loader.close()
