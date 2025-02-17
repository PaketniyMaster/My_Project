from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.config import settings
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
        except Exception:
            title = "Название отсутствует"

        # Ожидание загрузки данных отзывов (с добавлением явного ожидания)
        try:
            tooltip_text = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="user_reviews_summary_row"][2]')))
            tooltip_data = tooltip_text.get_attribute('data-tooltip-html')
            reviews = tooltip_data if tooltip_data else "Отзывов нет"
        except Exception:
            reviews = "Отзывов нет"

        # Дата выхода игры
        try:
            release_date = driver.find_element(By.CSS_SELECTOR, '#game_highlights .release_date .date').text
        except Exception:
            release_date = "Дата выхода отсутствует"

        print(f"Название: {title}")
        print(f"Отзывы: {reviews}")
        print(f"Дата выхода: {release_date}")

        # Скроллинг до самого низа страницы
        scroll_to_bottom(driver)

        # Переход к ссылке на отзывы, только если отзывы есть
        if reviews != "Отзывов нет":
            try:
                reviews_link = driver.find_element(By.XPATH, '//*[@id="ViewAllReviewssummary"]/a').get_attribute('href')
                reviews_link = reviews_link.replace("browsefilter=toprated", "browsefilter=trendsixmonths")
                print(f"Ссылка на отзывы: {reviews_link}")
                return reviews_link  # Возвращаем ссылку на страницу отзывов
            except Exception:
                print("Не удалось найти ссылку на отзывы.")
                return None
        else:
            print("Отзывы отсутствуют, пропускаем ссылку.")

    except Exception as e:
        print(f"Ошибка при парсинге страницы игры: {e}")
    finally:
        # Закрыть текущую вкладку и вернуться к основной
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
            get_game_details(driver, game_link)
            current_index += 1
        else:
            print(f"Элемент {current_index} не найден, прокручиваем страницу...")
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(random.uniform(2, 5))

def scroll_to_bottom(driver):
    """Скроллирует страницу до самого низа."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Дождаться загрузки контента
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # Если высота страницы не изменилась, значит, долистали до конца
            break
        last_height = new_height

if __name__ == "__main__":
    steam_url = settings.STEAM_URL
    #steam_url = "https://store.steampowered.com/search/?sort_by=Reviews_DESC&untags=492%2C872%2C44868%2C12095%2C21978%2C856791%2C9130%2C24904%2C10397%2C13906%2C5577%2C1445&category1=998&hidef2p=1&ndl=1"
    #steam_url = "https://store.steampowered.com/search/?sort_by=Released_DESC&untags=492%2C872%2C44868%2C12095%2C21978%2C856791%2C9130%2C24904%2C10397%2C13906%2C5577%2C1445&category1=998&hidef2p=1&ndl=1"
    driver = setup_driver()

    try:
        get_elements(driver, steam_url, 1, 10)
    finally:
        driver.quit()
