import csv
import time
import random
from selenium.webdriver.common.by import By

def get_games_list(driver, url, csv_filename="games.csv"):
    """Парсит список игр: получает название и ссылку, сохраняет в CSV."""
    driver.get(url)
    print(f"Открыта страница каталога: {url}")

    games = []
    current_index = 1  # Начинаем с первого элемента
    last_not_found = 0  # Счётчик подряд идущих отсутствующих элементов

    while last_not_found < 10:  # Если 10 подряд элементов не найдено, завершаем
        css_selector = f"#search_resultsRows > a:nth-child({current_index})"
        elements = driver.find_elements(By.CSS_SELECTOR, css_selector)

        if elements:
            game_link = elements[0].get_attribute("href")
            game_name = elements[0].find_element(By.CSS_SELECTOR, ".title").text
            games.append({"name": game_name, "link": game_link})
            print(f"Игра {current_index}: {game_name} - {game_link}")
            current_index += 1
            last_not_found = 0  # Сбрасываем счётчик отсутствующих элементов
        else:
            print(f"Элемент {current_index} не найден, прокручиваем страницу...")
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(random.uniform(2, 5))
            last_not_found += 1  # Увеличиваем счётчик отсутствующих элементов

    print("Игры закончились, завершаем парсинг.")

    # Сохранение в CSV
    if games:
        with open(csv_filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["name", "link"])
            writer.writeheader()
            writer.writerows(games)
        print(f"Данные сохранены в {csv_filename}")

    return games  # Возвращаем список игр
