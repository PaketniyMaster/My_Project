import csv
import locale
import re
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from app.database import engine
from app.models.game import Game

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")  # Устанавливаем русскую локаль
CSV_GAME_DETAILS = "game_details.csv"

def parse_date_custom(date_str):
    """Парсинг даты в формат datetime."""
    if not date_str or "Отзывов нет" in date_str:
        return None
    try:
        date_str = date_str.replace(" г.", "").strip()  # Убираем "г."
        date_str = re.sub(r"[^a-zA-Zа-яА-Я0-9 ]", " ", date_str)  # Убираем лишние символы

        month_map = {
            "янв": "01", "фев": "02", "мар": "03", "апр": "04",
            "май": "05", "июн": "06", "июл": "07", "авг": "08",
            "сен": "09", "окт": "10", "ноя": "11", "дек": "12"
        }

        parts = date_str.split()
        if len(parts) != 3:
            raise ValueError("Неправильный формат даты")

        day, month, year = parts
        month = month_map.get(month.lower(), month)  # Преобразуем месяц в числовой формат
        formatted_date = f"{year}-{month}-{day}"

        return datetime.strptime(formatted_date, "%Y-%m-%d")  # Преобразуем в объект datetime
    except Exception as e:
        print(f"⚠ Ошибка обработки даты: {date_str} ({e})")
        return None

def parse_reviews(review_text):
    """Парсинг процента положительных отзывов."""
    if "Отзывов нет" in review_text:
        return None
    try:
        percent = review_text.split("%")[0]
        return float(percent) if percent.isdigit() else None
    except:
        return None

def parse_genres(genres_text):
    """Парсинг жанров в строку с запятыми."""
    return genres_text.strip() if genres_text else None

def load_game_details():
    with open(CSV_GAME_DETAILS, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                game = session.query(Game).filter_by(name=row["title"]).one()
            except NoResultFound:
                print(f"❌ Игра '{row['title']}' не найдена. Пропускаем...")
                continue

            game.release_date = parse_date_custom(row["release_date"])  # Дата выхода
            game.positive_percent = parse_reviews(row["reviews"])  # Процент положительных отзывов
            game.tags = parse_genres(row["genres"])  # Жанры (tags)

    session.commit()  # ✅ Коммит после цикла
    print("✅ Данные об играх обновлены")

load_game_details()
session.close()
