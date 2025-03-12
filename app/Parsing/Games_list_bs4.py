import csv
import time
import random
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

CSV_FILE = "games.csv"
MAX_THREADS = 10

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/537.36",
]

def get_random_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def fetch_page(start):
    url = "https://store.steampowered.com/search/results/"
    params = {
        "start": start,
        "count": 100,
        "sort_by": "Released_DESC",
        "category1": 998,
        "snr": "1_7_7_230_7",
        "hidef2p": 1,
        "infinite": 1,
        "untags": "492,872,44868,12095,21978,856791,9130,24904,10397,13906,5577,1445",
    }

    try:
        response = requests.get(url, headers=get_random_headers(), params=params, timeout=15)
        if response.status_code != 200:
            print(f"Ошибка {response.status_code} на странице {start}")
            return []

        data = response.json()
        soup = BeautifulSoup(data["results_html"], "html.parser")
        games = soup.select(".search_result_row")

        return [{"title": game.select_one(".title").text.strip(), "link": game["href"]} for game in games]

    except Exception as e:
        print(f"Ошибка при загрузке страницы {start}: {e}")
        return []

def fetch_all_games():
    all_games = []
    start = 0
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        while True:
            futures = [executor.submit(fetch_page, start + i * 100) for i in range(MAX_THREADS)]
            new_games = []

            for future in as_completed(futures):
                result = future.result()
                if result:
                    new_games.extend(result)

            if not new_games:
                break

            all_games.extend(new_games)
            start += MAX_THREADS * 100
            print(f"✅ Собрано игр: {len(all_games)}")

    return all_games

def save_to_csv(games):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "link"])
        writer.writeheader()
        writer.writerows(games)

games = fetch_all_games()
print(f"🎮 Итог: собрано игр: {len(games)}")
save_to_csv(games)
