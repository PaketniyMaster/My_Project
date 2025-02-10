import csv
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def parse_reviews_from_row(row_element):
    reviews = []
    try:
        review_elements = row_element.find_elements(By.XPATH, './/div[@class="apphub_CardContentMain"]')
        for review_element in review_elements:
            try:
                review_text = review_element.text.strip()
                if review_text and review_text not in reviews:
                    reviews.append(review_text)
            except Exception as e:
                print(f"Ошибка при извлечении текста отзыва: {e}")
    except Exception as e:
        print(f"Ошибка при обработке строки с отзывами: {e}")
    return reviews

def parse_page_reviews(driver):
    reviews = []
    try:
        row_elements = driver.find_elements(By.XPATH, '//div[contains(@id, "page_") and contains(@id, "_row")]')
        print(f"Найдено строк с отзывами: {len(row_elements)}")
        for row in row_elements:
            reviews += parse_reviews_from_row(row)
    except Exception as e:
        print(f"Ошибка при парсинге страницы: {e}")
    return reviews

def scroll_to_load_reviews(driver):
    max_scroll_attempts = 5  # Максимальное количество попыток прокрутки
    scroll_step = 800  # Высота прокрутки за одну итерацию

    last_review_count = 0  # Для отслеживания, загружаются ли новые отзывы
    attempt = 0

    while attempt < max_scroll_attempts:
        driver.execute_script(f"window.scrollBy(0, {scroll_step});")
        time.sleep(1.5)  # Даем время странице подгрузить данные
        
        new_reviews = len(driver.find_elements(By.XPATH, '//div[contains(@id, "page_") and contains(@id, "_row")]'))
        
        if new_reviews > last_review_count:
            last_review_count = new_reviews
            attempt = 0  # Сбрасываем попытки, если появились новые отзывы
        else:
            attempt += 1  # Увеличиваем счетчик, если новых отзывов не появилось
        
        print(f"Прокрутка {attempt}/{max_scroll_attempts} | Отзывов загружено: {new_reviews}")

    print("Все отзывы загружены.")
    return last_review_count > 0  # Возвращает True, если были загружены какие-то отзывы

def parse_all_reviews(driver):
    """Парсит отзывы по ссылкам из game_details.csv."""
    input_csv = "game_details.csv"
    output_csv = "reviews.csv"

    with open(input_csv, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        games = [row for row in reader if row.get("review_link") and row["review_link"] != "Нет ссылки"]

    if not games:
        print("Нет доступных игр для парсинга отзывов.")
        return

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["game_title", "review_text"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for game in games:
            game_title = game["title"]
            review_url = game["review_link"]
            driver.get(review_url)
            time.sleep(3)

            all_reviews = []

            try:
                print(f"Загружаем все отзывы для {game_title}...")
                
                if scroll_to_load_reviews(driver):
                    all_reviews = parse_page_reviews(driver)

            except Exception as e:
                print(f"Ошибка при парсинге {game_title}: {e}")

            unique_reviews = list(set(all_reviews))
            print(f"Всего отзывов для {game_title}: {len(unique_reviews)}")

            for review in unique_reviews:
                writer.writerow({"game_title": game_title, "review_text": review})

    print("Парсинг завершен. Отзывы сохранены в reviews.csv")
