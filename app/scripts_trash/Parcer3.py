from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# Настройка Selenium WebDriver
def setup_driver():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; Pixel 4 XL Build/QD1A.190805.028) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36"
    ]
    user_agent = random.choice(user_agents)
    print(f"Используется User-Agent: {user_agent}")

    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")

    service = Service('D:\\VSC Projects\\WebDriver\\chromedriver-win64(1)\\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
    


def simulate_user_actions(driver):
    actions = ActionChains(driver)
    actions.move_by_offset(random.randint(5, 20), random.randint(5, 20)).perform()  # Случайное движение мыши
    driver.execute_script("window.scrollBy(0, window.innerHeight);")  # Прокрутка вниз
    time.sleep(random.uniform(1, 3))  # Случайная задержка


def wait_for_element(driver, xpath):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )

def parse_metacritic(driver, url):
    try:
        for page in range(1, 6):  # Пример: 5 страниц
            page_url = url.replace("page=1", f"page={page}")
            driver.get(page_url)
            print(f"Открыта страница: {page_url}")

            # Ожидание загрузки страницы
            wait_for_element(driver, "//h1")  # Пример ожидания главного заголовка

            for i in range(1, 25):  # Для 24 элементов
                try:
                    xpath = f"//*[@id='__layout']/div/div[2]/div[1]/main/section/div[3]/div[{1 if i <= 12 else 3}]/div[{i if i <= 12 else i-12}]/a"
                    element = driver.find_element(By.XPATH, xpath)

                    # Имитация наведения мыши
                    ActionChains(driver).move_to_element(element).perform()
                    time.sleep(random.uniform(1, 2))  # Короткая пауза

                    # Извлечение ссылки
                    game_link = element.get_attribute("href")
                    print(f"Ссылка на игру {i}: {game_link}")

                    # Открытие в новой вкладке
                    driver.execute_script("window.open(arguments[0], '_blank');", game_link)
                    driver.switch_to.window(driver.window_handles[-1])
                    
                    # Задержка для загрузки страницы
                    time.sleep(random.uniform(3, 6))

                    # Извлечение данных
                    try:
                        title = driver.find_element(By.XPATH, "//h1").text
                        metascore = driver.find_element(By.XPATH, "//div[contains(@class, 'metascore_w')]").text
                        user_score = driver.find_element(By.XPATH, "//div[contains(text(),'User Score')]/following-sibling::div").text
                        print(f"Название игры: {title}")
                        print(f"Metascore: {metascore}")
                        print(f"User Score: {user_score}")
                    except Exception as e:
                        print(f"Ошибка при извлечении данных: {e}")

                    # Закрытие вкладки и возвращение к исходной
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                except Exception as e:
                    print(f"Ошибка при обработке элемента {i}: {e}")
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")


def parse_steam(driver, url):
    try:
        driver.get(url)
        print(f"Открыта страница: {url}")

        # Задержка для загрузки динамических элементов
        time.sleep(2)  

        i = 1
        while True:
            try:
                css_selector = f"#search_resultsRows > a:nth-child({i}) > div.responsive_search_name_combined > div.col.search_name.ellipsis > span"
                element = driver.find_element(By.CSS_SELECTOR, css_selector)
                print(f"Элемент {i}: {element.text}")
                i += 1
            except Exception:
                print("Достигнут конец списка элементов.")
                break

    except Exception as e:
        print(f"Ошибка при парсинге: {e}")

if __name__ == "__main__":
    # Укажите URL для парсинга
    metacritic_url = "https://www.metacritic.com/browse/game/pc/all/all-time/metascore/?releaseYearMin=2000&releaseYearMax=2025&platform=pc&genre=action&genre=action-adventure&genre=action-puzzle&genre=action-rpg&genre=adventure&genre=arcade&genre=board-or-card-game&genre=first---person-shooter&genre=card-battle&genre=fighting&genre=rpg&genre=open---world&genre=mmorpg&genre=platformer&genre=puzzle&genre=racing&genre=real---time-strategy&genre=roguelike&genre=survival&genre=sports&genre=simulation&genre=shooter&genre=strategy&genre=sandbox&genre=rhythm&genre=tactics&genre=third---person-shooter&page=1"
    steam_url = "https://store.steampowered.com/search/?sort_by=Released_DESC&untags=492%2C4182%2C5611%2C872&category1=998&hidef2p=1&ndl=1"

    # Настройка драйвера
    driver = setup_driver()

    try:
        # Парсинг Metacritic
        parse_metacritic(driver, metacritic_url)

        # Парсинг Steam
        #parse_steam(driver, steam_url)

    finally:
        # Закрытие драйвера
        driver.quit()

