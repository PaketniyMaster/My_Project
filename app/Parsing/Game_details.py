import csv
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

CSV_GAMES = "games.csv"
CSV_GAME_DETAILS = "game_details.csv"

def handle_age_check(driver):
    """Проверяет страницу на наличие проверки возраста и вводит дату рождения."""
    if "agecheck" in driver.current_url:
        print("Обнаружена проверка возраста. Заполняем форму...")
        try:
            Select(driver.find_element(By.ID, "ageDay")).select_by_value("1")
            Select(driver.find_element(By.ID, "ageMonth")).select_by_value("April")
            Select(driver.find_element(By.ID, "ageYear")).select_by_value("2005")
            submit_button = driver.find_element(By.ID, "view_product_page_btn")
            driver.execute_script("arguments[0].click();", submit_button)
            time.sleep(3)
            print("Возраст успешно введен.")
        except Exception as e:
            print(f"Ошибка при вводе возраста: {e}")

def remove_language_filter(driver):
    """Убирает фильтр 'Ваши языки', если он активен."""
    try:
        language_filter = driver.find_element(By.ID, "reviews_filter_language")
        driver.execute_script("arguments[0].click();", language_filter)
        time.sleep(2)
        print("🔄 Фильтр 'Ваши языки' отключен.")
    except:
        print("✅ Фильтр 'Ваши языки' отсутствует, пропускаем.")

def check_russian_support(driver):
    """Проверяет, поддерживается ли русский язык."""
    try:
        language_status = driver.find_element(By.XPATH, '//*[@id="languageTable"]/table/tbody/tr[2]/td[2]').text.strip()
        return "✔" in language_status
    except:
        return False

def get_genres(driver):
    """Извлекает список жанров игры."""
    try:
        genre_elements = driver.find_elements(By.XPATH, '//*[@id="genresAndManufacturer"]/span')
        genres = [genre.text for genre in genre_elements]
        return ", ".join(genres) if genres else "Не указаны"
    except:
        return "Ошибка извлечения жанров"

def get_game_details(driver, game_url):
    """Открывает страницу игры и парсит её данные."""
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
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
            has_reviews = True
        except:
            reviews = "Отзывов нет"
            has_reviews = False
        if has_reviews:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            try:
                reviews_link = driver.find_element(By.XPATH, '//*[@id="ViewAllReviewssummary"]/a').get_attribute('href')
                reviews_link = reviews_link.replace("browsefilter=toprated", "browsefilter=trendsixmonths")
            except:
                reviews_link = "Нет ссылки"
        else:
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
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

def save_game_details_to_csv(details_list):
    """Сохраняет данные об играх в CSV."""
    with open(CSV_GAME_DETAILS, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["title", "release_date", "reviews", "russian_supported", "genres", "review_link"])
        writer.writeheader()
        writer.writerows(details_list)

def parse_all_games(driver, csvu):
    """Читает ссылки из games.csv и парсит данные об играх."""
    details_list = []
    with open(csvu, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            game_url = row["link"]
            game_details = get_game_details(driver, game_url)
            if game_details:
                details_list.append(game_details)
    save_game_details_to_csv(details_list)
    print("✅ Данные об играх сохранены в game_details.csv")
