import csv
import re
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from app.database import engine
from app.models.game import Game
from app.models.review import Review

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

CSV_REVIEWS = "reviews.csv"

def clean_review(text):
    """Удаляет ненужные строки и оставляет только текст отзыва."""
    patterns_to_remove = [
        r"Пользовател[ейь]?.*посчитал[и]?.*обзор полезным.*",  # Убираем строки про полезность
        r"Ещё никто не посчитал этот обзор полезным.*",  # Убираем пустые отзывы
        r"Пользовател[ейь]?.*посчитал[и]?.*обзор полезным.*",  
        r"Пользователей, посчитавших обзор полезным: \d+ \d+",
        r"Пользователей, посчитавших обзор полезным: \d+",
        r"Пользователей, посчитавших обзор забавным: \d+ \d+",
        r"Пользователей, посчитавших обзор забавным: \d+",
        r".*пользовател[ейь]?.*посчитал[и]? этот обзор полезным.*",  # Удаляем строки про полезность
        r".*пользовател[ейь]?.*посчитал[и]? этот обзор забавным.*",  # Удаляем строки про забавность
        r"^\d+\s+.*",  # Удаляем одиночные числа в начале строки
        r"\d+ ч. всего.*",  # Удаляем строки с количеством часов
        r"Опубликовано:.*",  # Удаляем дату публикации
        r"ОБЗОР ПРОДУКТА В РАННЕМ ДОСТУПЕ.*",  # Удаляем отметку о раннем доступе
        r"На этот обзор есть ответ от разработчика.*",  # Удаляем строки про ответы разработчиков
        r"Товар получен бесплатно",  # Удаляем строку про бесплатный товар
        r"Have requested a refund\.",  # Удаляем про возврат
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)

    # Повторно удаляем возможные числа, которые остались
    text = re.sub(r"^\d+\.\s*", "", text, flags=re.MULTILINE)  # "10. Текст" → "Текст"
    text = re.sub(r"^\d+\s*", "", text, flags=re.MULTILINE)  # "18 Текст" → "Текст"

    # Убираем пустые строки
    text = re.sub(r"\n\s*\n", "\n", text).strip()

    return text

def extract_rating(text):
    """Определяет рейтинг отзыва (1 - положительный, 0 - отрицательный)."""
    if "Рекомендую" in text:
        return 1
    if "Не рекомендую" in text:
        return 0
    return None

def process_review_text(text):
    """Удаляет 'Рекомендую' и 'Не рекомендую' из текста отзыва."""
    text = re.sub(r"^(Рекомендую|Не рекомендую)\s*", "", text, flags=re.MULTILINE)
    return text.strip()

def load_reviews():
    with open(CSV_REVIEWS, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                game = session.query(Game).filter_by(name=row["game_title"]).one()
            except NoResultFound:
                print(f"❌ Игра '{row['game_title']}' не найдена. Пропускаем...")
                continue

            original_text = row["review_text"]
            rating = extract_rating(original_text)  # Получаем рейтинг
            review_text = clean_review(original_text)  # Удаляем лишнее
            review_text = process_review_text(review_text)  # Убираем "Рекомендую"

            if review_text:  # Пропускаем пустые отзывы
                review = Review(game_id=game.id, review_text=review_text, rating=rating)
                session.add(review)

    session.commit()
    print("✅ Отзывы загружены в БД")

load_reviews()
session.close()
