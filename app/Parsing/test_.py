import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import sys

BASE_URL = "https://www.russianfood.com"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
]

HEADERS_TEMPLATE = {
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": BASE_URL,
    "Connection": "keep-alive",
}

def safe_get(url, max_retries=3):
    for attempt in range(max_retries):
        headers = HEADERS_TEMPLATE.copy()
        headers["User-Agent"] = random.choice(USER_AGENTS)
        try:
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code in (403, 429):
                print(f"[!] Статус {res.status_code} — возможно бан. URL: {url}")
                print("[✗] Парсинг остановлен из-за возможного бана.")
                sys.exit(1)
            time.sleep(random.uniform(1.5, 4.0))
            return res
        except Exception as e:
            print(f"[X] Ошибка при подключении: {e}")
            time.sleep(random.uniform(2.0, 5.0))
            continue

    print(f"[✗] Все попытки получить {url} не удались.")
    return None

def get_recipe_links_from_page(page):
    url = f"{BASE_URL}/recipes/bytype/?fid=3&page={page}"
    response = safe_get(url)
    if not response:
        return []

    response.encoding = 'windows-1251'
    soup = BeautifulSoup(response.text, "html.parser")
    links = []

    for a in soup.find_all("a"):
        href = a.get("href")
        if href and "/recipes/recipe.php" in href:
            full_link = BASE_URL + href
            if full_link not in links:
                links.append(full_link)

    return links

def parse_recipe(link):
    res = safe_get(link)
    if not res:
        return []

    soup = BeautifulSoup(res.content, "html.parser")

    title_tag = soup.find("h1")
    title = title_tag.text.strip() if title_tag else "Без названия"

    ingr_table = soup.find("table", class_="ingr")
    if not ingr_table:
        print(f"[!] Нет ингредиентов: {link}")
        return []

    spans = ingr_table.find_all("span")
    result = []
    for span in spans:
        text = span.text.strip()
        if " – " in text:
            name, amount = text.split(" – ", 1)
        elif " - " in text:
            name, amount = text.split(" - ", 1)
        else:
            name = text
            amount = ""
        result.append([title, name.strip(), amount.strip(), link])

    return result

def main():
    max_pages = 50
    print(f"[+] Сбор ссылок с {max_pages} страниц...")
    all_links = []

    for page in range(1, max_pages + 1):
        links = get_recipe_links_from_page(page)
        if not links:
            print(f"[!] Страница {page} пуста — остановка.")
            break
        all_links.extend(links)
        print(f"[✓] Страница {page} — найдено {len(links)} ссылок.")
        time.sleep(random.uniform(2.0, 6.0))  # задержка между страницами

    print(f"[+] Всего рецептов: {len(all_links)}. Парсинг...")

    data = []
    for idx, url in enumerate(all_links, 1):
        print(f"[{idx}/{len(all_links)}] Парсинг: {url}")
        result = parse_recipe(url)
        if result:
            data.extend(result)
        time.sleep(random.uniform(1.0, 3.5))  # задержка между рецептами

    print(f"[✓] Сохранение {len(data)} записей в CSV...")

    with open("recipes_safe.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["title", "ingredient_name", "ingredient_amount", "link"])
        writer.writerows(data)

    print("[✓] Готово! Файл: recipes_safe.csv")

if __name__ == "__main__":
    main()
