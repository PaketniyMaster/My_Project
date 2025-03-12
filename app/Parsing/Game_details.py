import csv
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
from app.Parsing.Driver import setup_driver  # Импортируем функцию для создания драйвера
from concurrent.futures import ThreadPoolExecutor, as_completed

CSV_GAMES = "games_test.csv"
CSV_GAME_DETAILS = "game_details_test.csv"
NUM_THREADS = 10  # Количество одновременно работающих браузеров

def handle_age_check(driver):
    if "agecheck" in driver.current_url:
        try:
            Select(driver.find_element(By.ID, "ageDay")).select_by_value("1")
            Select(driver.find_element(By.ID, "ageMonth")).select_by_value("April")
            Select(driver.find_element(By.ID, "ageYear")).select_by_value("2005")
            submit_button = driver.find_element(By.ID, "view_product_page_btn")
            driver.execute_script("arguments[0].click();", submit_button)
            time.sleep(3)
        except Exception as e:
            print(f"Ошибка при вводе возраста: {e}")

def remove_language_filter(driver):
    try:
        language_filter = driver.find_element(By.ID, "reviews_filter_language")
        driver.execute_script("arguments[0].click();", language_filter)
        time.sleep(2)
    except:
        pass

def check_russian_support(driver):
    try:
        language_status = driver.find_element(By.XPATH, '//*[@id="languageTable"]/table/tbody/tr[2]/td[2]').text.strip()
        return "✔" in language_status
    except:
        return False

def get_genres(driver):
    try:
        genre_elements = driver.find_elements(By.XPATH, '//*[@id="genresAndManufacturer"]/span')
        return ", ".join([genre.text for genre in genre_elements]) if genre_elements else "Не указаны"
    except:
        return "Ошибка извлечения жанров"

def get_game_details(driver, game_url):
    driver.get(game_url)
    handle_age_check(driver)
    remove_language_filter(driver)
    
    try:
        wait = WebDriverWait(driver, 10)
        title = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="appHubAppName"]'))).text
        release_date = driver.find_element(By.CSS_SELECTOR, '#game_highlights .release_date .date').text
        
        try:
            tooltip_text = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="user_reviews_summary_row"][2]')))
            reviews = tooltip_text.get_attribute('data-tooltip-html') or "Отзывов нет"
        except:
            reviews = "Отзывов нет"
        
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 3))
            reviews_link = driver.find_element(By.XPATH, '//*[@id="ViewAllReviewssummary"]/a').get_attribute('href')
            reviews_link = reviews_link.replace("browsefilter=toprated", "browsefilter=trendsixmonths")
        except:
            reviews_link = "Нет ссылки"

        russian_supported = check_russian_support(driver)
        genres = get_genres(driver)

        return {
            "title": title,
            "release_date": release_date,
            "reviews": reviews,
            "russian_supported": "Да" if russian_supported else "Нет",
            "genres": genres,
            "review_link": reviews_link,
        }
    except Exception as e:
        print(f"Ошибка при парсинге {game_url}: {e}")
        return None
    finally:
        driver.quit()

def save_game_details_to_csv(details_list):
    with open(CSV_GAME_DETAILS, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "release_date", "reviews", "russian_supported", "genres", "review_link"])
        writer.writeheader()
        writer.writerows(details_list)

def process_url(url):
    driver = setup_driver()  # Создаём новый экземпляр драйвера для каждого потока
    try:
        return get_game_details(driver, url)  # Парсим страницу
    finally:
        driver.quit()  # Обязательно закрываем браузер после работы

def parse_games_multithreaded():
    start_time = time.time()
    
    with open(CSV_GAMES, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        game_urls = [row["link"] for row in reader]

    details_list = []
    
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = {executor.submit(process_url, url): url for url in game_urls}

        for future in as_completed(futures):
            result = future.result()
            if result:
                details_list.append(result)

    save_game_details_to_csv(details_list)
    print(f"⏳ Время обработки {len(game_urls)} игр: {time.time() - start_time:.2f} сек.")
    print("✅ Данные об играх сохранены в game_details.csv")
