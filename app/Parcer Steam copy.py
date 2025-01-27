from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Случайный User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    # Укажите путь к chromedriver
    service = Service('D:\\VSC Projects\\WebDriver\\chromedriver-win64\\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver


def get_game_details(driver, game_url):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(game_url)

    try:
        # Ожидание загрузки страницы
        wait = WebDriverWait(driver, 10)

        # Название игры
        try:
            title = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="appHubAppName"]'))).text
        except:
            title = "Название отсутствует"

        # Процент положительных отзывов
        try:
            reviews = driver.find_element(By.XPATH, '//*[@id="userReviews"]/div/div[2]/span[3]').text
        except:
            reviews = "Нет отзывов"

        # Дата выхода игры
        try:
            release_date = driver.find_element(By.CSS_SELECTOR, '#game_highlights .release_date .date').text
        except:
            release_date = "Дата выхода отсутствует"

        print(f"Название: {title}")
        print(f"Отзывы: {reviews}")
        print(f"Дата выхода: {release_date}")
    except Exception as e:
        print(f"Ошибка при парсинге страницы игры: {e}")
    finally:
        # Проверить наличие основной вкладки
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

def get_elements(driver, url, start_index, end_index):
    driver.get(url)
    print(f"Открыта страница: {url}")

    current_index = start_index
    while current_index <= end_index:
        css_selector = f"#search_resultsRows > a:nth-child({current_index})"
        elements = driver.find_elements(By.CSS_SELECTOR, css_selector)

        if elements:
            game_link = elements[0].get_attribute("href")
            print(f"Ссылка на игру {current_index}: {game_link}")

            # Переход по ссылке игры для извлечения информации
            get_game_details(driver, game_link)
            current_index += 1
        else:
            print(f"Элемент {current_index} не найден, прокручиваем страницу...")
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    steam_url = "https://store.steampowered.com/search/?sort_by=Reviews_DESC&untags=492%2C872%2C44868%2C12095%2C21978%2C856791%2C9130%2C24904%2C10397%2C13906%2C5577%2C1445&category1=998&hidef2p=1&ndl=1"
    driver = setup_driver()

    try:
        get_elements(driver, steam_url, 1, 10)  # Измените диапазон на желаемый
    finally:
        driver.quit()
