import csv
import os
import time
import random
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

CSV_GAMES = r"D:\VSC Projects\App\Project\app\csv\NICE.csv"
CSV_GAME_DETAILS = r"D:\VSC Projects\App\Project\app\csv\NICE_details.csv"
NUM_THREADS = 10  
MAX_GAMES = 25005  
SAVE_EVERY = 500  
START_FROM = 0

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/537.36",
]

def get_random_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def get_game_details(game_url, session):
    try:
        response = session.get(game_url, headers=get_random_headers(), timeout=10)
        if response.status_code != 200:
            print(f"Ошибка {response.status_code} при загрузке {game_url}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("div", {"id": "appHubAppName"})
        title = title.text.strip() if title else "Не найдено"

        release_date = soup.select_one("#game_highlights .release_date .date")
        release_date = release_date.text.strip() if release_date else "Не указана"

        genres = soup.select("#genresAndManufacturer span")
        genres = ", ".join([g.text.strip() for g in genres]) if genres else "Не указаны"

        russian_supported = soup.select_one("#languageTable tr:nth-of-type(2) td:nth-of-type(2)")
        russian_supported = "Да" if russian_supported and "✔" in russian_supported.text else "Нет"

        # Парсинг описания
        description = soup.select_one(".game_description_snippet")
        description = description.text.strip() if description else "Описание не найдено"

        review_summary = soup.select(".user_reviews_summary_row")

        reviews = "Отзывов нет"

        for review in review_summary:
            subtitle = review.select_one(".subtitle")
            if subtitle and "All Reviews" in subtitle.text:
                tooltip = review.get("data-tooltip-html")
                review_text = review.select_one(".game_review_summary")
                review_count = review.select_one(".responsive_hidden")
                short_review = review.select_one(".responsive_reviewdesc_short")

                reviews = ""
                if review_text:
                    reviews += review_text.text.strip()
                if review_count:
                    reviews += f" ({review_count.text.strip()})"
                if tooltip:
                    reviews += f" - {tooltip.strip()}"
                elif short_review:
                    reviews += f" - {short_review.text.strip()}"
                break
            
        return {
            "title": title,
            "release_date": release_date,
            "reviews": reviews,
            "russian_supported": russian_supported,
            "genres": genres,
            "description": description,
            "review_link": game_url + "/#all_reviews"
        }
    except Exception as e:
        print(f"Ошибка при парсинге {game_url}: {e}")
        return None


def save_game_details_to_csv(details_list, append=False):
    mode = "a" if append else "w"
    with open(CSV_GAME_DETAILS, mode=mode, newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "release_date", "reviews", "russian_supported", "genres", "description", "review_link"])
        if not append:
            writer.writeheader()
        writer.writerows(details_list)

def parse_games_multithreaded():
    start_time = time.time()
    
    with open(CSV_GAMES, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        game_urls = [row["link"] for i, row in enumerate(reader) if i >= START_FROM][:MAX_GAMES]  

    details_list = []
    
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            futures = {executor.submit(get_game_details, url, session): url for url in game_urls}

            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                if result:
                    details_list.append(result)

                if (i + 1) % SAVE_EVERY == 0:
                    save_game_details_to_csv(details_list, append=True)
                    details_list.clear()
                    print(f"✅ Сохранено {i + 1 + START_FROM}/{MAX_GAMES + START_FROM} игр")

                time.sleep(random.uniform(0.2, 0.5))  

    if details_list:
        save_game_details_to_csv(details_list, append=True)

    print(f"⏳ Время обработки {MAX_GAMES} игр: {time.time() - start_time:.2f} сек.")
    print("✅ Данные сохранены.")

