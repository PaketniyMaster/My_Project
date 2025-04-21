import asyncio
import aiohttp
import requests
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Настройки
NUM_THREADS = 10
MAX_CONCURRENT_REVIEWS = 10
SLEEP_TIME = 0.1
SAVE_EVERY = 1
MAX_REVIEWS_PER_GAME = 50000
input_file = r"D:\VSC Projects\App\Project\app\csv\NICE_details copy.csv"
output_file = r"D:\VSC Projects\App\Project\app\csv\NICE_reviews1.csv"
start_row = 0

def get_app_id(link):
    try:
        return link.split("/app/")[1].split("/")[0]
    except IndexError:
        return None

async def fetch_reviews(session, app_id, cursor):
    url = f"https://store.steampowered.com/appreviews/{app_id}"
    params = {
        "json": 1,
        "filter": "recent",
        "language": "all",
        "review_type": "all",
        "purchase_type": "all",
        "num_per_page": 500,
        "cursor": cursor
    }

    try:
        async with session.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"}) as response:
            if response.status != 200:
                print(f"Ошибка {response.status} при запросе отзывов для {app_id}")
                return None, cursor

            data = await response.json()
            return data.get("reviews", []), data.get("cursor", "").strip()
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return None, cursor

async def parse_reviews(app_id, game_title):
    reviews = []
    cursor = "*"
    
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REVIEWS)
    async with aiohttp.ClientSession(connector=connector) as session:
        while True:
            new_reviews, new_cursor = await fetch_reviews(session, app_id, cursor)

            if new_reviews:
                for r in new_reviews:
                    if len(reviews) >= MAX_REVIEWS_PER_GAME:
                        print(f"⚠️ [DEBUG] Достигнут лимит отзывов для {game_title}")
                        return reviews
                    review_text = r.get("review", "Отзыв отсутствует")
                    review_type = "Положительный" if r.get("voted_up") else "Отрицательный"
                    reviews.append((game_title, review_type, review_text))

            if not new_cursor or new_cursor == cursor:
                print(f"✅ [DEBUG] Достигнут конец отзывов для {game_title}")
                break

            cursor = new_cursor
            await asyncio.sleep(SLEEP_TIME)

    return reviews

def process_game(row):
    if "%" not in row["reviews"]:
        return None

    app_id = get_app_id(row["review_link"])
    if not app_id:
        print(f"❌ Ошибка: не удалось получить app_id для {row['title']}")
        return None

    game_title = row["title"]
    print(f"[{game_title}] Начинаем парсинг...")

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        game_reviews = loop.run_until_complete(parse_reviews(app_id, game_title))
    finally:
        if not loop.is_closed():
            loop.close()

    print(f"[{game_title}] Спарсено {len(game_reviews)} отзывов")
    return game_reviews

def parse_steam_reviews(input_file, output_file, start_row=0):
    start_time = time.time()
    games_processed = 0
    total_reviews = 0
    temp_storage = []

    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "a", encoding="utf-8", newline="") as outfile:
        reader = csv.DictReader(infile)
        writer = csv.writer(outfile, delimiter=";")

        if start_row == 0:
            writer.writerow(["game_title", "review_type", "review_text"])

        for _ in range(start_row):
            next(reader, None)

        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futures = {executor.submit(process_game, row): row for row in reader}

            for future in as_completed(futures):
                game_reviews = future.result()
                if game_reviews:
                    temp_storage.extend(game_reviews)
                    total_reviews += len(game_reviews)
                    games_processed += 1

                if games_processed % SAVE_EVERY == 0 and temp_storage:
                    writer.writerows(temp_storage)
                    temp_storage.clear()
                    print(f"💾 Сохранены {games_processed} игр")

    if temp_storage:
        writer.writerows(temp_storage)

    end_time = time.time()
    print(f"\n✅ Обработано игр: {games_processed}")
    print(f"💬 Всего отзывов: {total_reviews}")
    print(f"⏳ Время работы: {round(end_time - start_time, 2)} сек")

if __name__ == "__main__":
    parse_steam_reviews(input_file, output_file, start_row)
