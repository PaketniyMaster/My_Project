import csv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from app.database import engine
from app.models.game import Game
from app.models.game_summary import GameSummary  # предполагается, что модель называется GameSummary и импортируется отсюда

SessionLocal = sessionmaker(bind=engine)

CSV_SUMMARIES = r"D:\VSC Projects\App\Project\app\csv\summaries_NICE2.csv"

def load_summaries():
    session = SessionLocal()
    try:
        with open(CSV_SUMMARIES, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                game_title = row["game_title"]

                game = session.query(Game).filter(func.lower(Game.name) == game_title.lower()).first()

                if not game:
                    print(f"⛔ Игра '{game_title}' не найдена в БД, пропускаем.")
                    continue

                # Добавляем русскую версию
                if row["summary_ru"]:
                    summary_ru = GameSummary(
                        game_id=game.id,
                        summary=row["summary_ru"],
                        language="ru"
                    )
                    session.add(summary_ru)

                # Добавляем английскую версию
                if row["summary_en"]:
                    summary_en = GameSummary(
                        game_id=game.id,
                        summary=row["summary_en"],
                        language="en"
                    )
                    session.add(summary_en)

                session.commit()
                print(f"✅ Сводки для '{game_title}' загружены")

        print("🎉 Загрузка завершена")
    finally:
        session.close()

load_summaries()
