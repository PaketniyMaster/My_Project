from transformers import MBartForConditionalGeneration, MBart50Tokenizer
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.game import Game
from app.models.review import Review
from app.models.game_summary import GameSummary
from langdetect import detect
from collections import defaultdict
from datetime import datetime
import re

# --- модель и токенайзер ---
model_name = "facebook/mbart-large-50-many-to-many-mmt"
tokenizer = MBart50Tokenizer.from_pretrained(model_name)
model = MBartForConditionalGeneration.from_pretrained(model_name)

# --- фильтрация ---
def is_valid_review(text: str) -> bool:
    if not text or len(text.strip()) < 20:
        return False
    if len(re.findall(r'\w+', text)) < 5:
        return False
    if re.fullmatch(r"[\W\d_]+", text):
        return False
    return True

def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        if lang == "ru":
            return "ru"
        elif lang == "en":
            return "en"
    except:
        return None

def split_reviews_by_lang(reviews_texts):
    lang_groups = defaultdict(list)
    for review in reviews_texts:
        if is_valid_review(review):
            lang = detect_language(review)
            if lang:
                lang_groups[lang].append(review)
    return lang_groups

# --- суммаризация ---
def summarize_text(text, max_input_len=1024, max_output_len=100):
    inputs = tokenizer(text, return_tensors="pt", max_length=max_input_len, truncation=True)
    summary_ids = model.generate(**inputs, max_length=max_output_len, min_length=20, length_penalty=2.0, num_beams=4)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def summarize_reviews(reviews, batch_size=500):
    partial_summaries = []
    for i in range(0, len(reviews), batch_size):
        batch = reviews[i:i+batch_size]
        text = " ".join(batch)
        summary = summarize_text(text)
        partial_summaries.append(summary)
    return summarize_text(" ".join(partial_summaries))

# --- сохранить в БД ---
def save_summary(db: Session, game_id: int, summary_text: str, language: str = "ru"):
    existing = db.query(GameSummary).filter_by(game_id=game_id, language=language).first()
    if existing:
        existing.summary = summary_text
        existing.updated_at = datetime.utcnow()
    else:
        db.add(GameSummary(game_id=game_id, summary=summary_text, language=language))
    db.commit()

# --- тест на одной игре ---
def summarize_game(game_id: int):
    db = SessionLocal()
    reviews = db.query(Review.review_text).filter(Review.game_id == game_id).all()
    reviews_texts = [r.review_text for r in reviews]
    lang_groups = split_reviews_by_lang(reviews_texts)

    for lang, texts in lang_groups.items():
        if len(texts) < 10:
            print(f"[{lang}] мало отзывов: {len(texts)} — пропуск")
            continue
        tokenizer.src_lang = "ru_RU" if lang == "ru" else "en_XX"
        print(f"Суммаризация ({lang}), отзывов: {len(texts)}")
        try:
            summary = summarize_reviews(texts)
            print(f"СУММАРИ ({lang}):\n{summary}\n")
            save_summary(db, game_id, summary, language=lang)
        except Exception as e:
            print(f"[!] Ошибка: {e}")
    db.close()

if __name__ == "__main__":
    test_game_id = 7852  # Укажи ID игры с небольшим числом отзывов
    summarize_game(test_game_id)
