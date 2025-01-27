from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

# Настройка Selenium WebDriver
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Изменение User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    ]
    user_agent = random.choice(user_agents)
    chrome_options.add_argument(f"user-agent={user_agent}")
    
    # Укажите путь к chromedriver
    service = Service('D:\VSC Projects\WebDriver\chromedriver-win64\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def simulate_user_actions(driver):
    actions = ActionChains(driver)
    actions.move_by_offset(random.randint(5, 20), random.randint(5, 20)).perform()  # Случайное движение мыши
    driver.execute_script("window.scrollBy(0, window.innerHeight);")  # Прокрутка вниз
    time.sleep(random.uniform(1, 3))  # Случайная задержка

    
# Основная функция парсинга
def parse_metacritic(driver, url):
    try:
        for page in range(1, 6):  # Для примера, парсим 5 страниц
            page_url = url.replace("page=1", f"page={page}")
            driver.get(page_url)
            print(f"Открыта страница: {page_url}")

            # Задержка для загрузки динамических элементов
            time.sleep(random.uniform(2, 4))  # Случайная задержка

            for i in range(1, 25):
                try:
                    # Определяем XPath в зависимости от позиции элемента
                    if i <= 12:
                        xpath = f'//*[@id="__layout"]/div/div[2]/div[1]/main/section/div[3]/div[1]/div[{i}]/a'
                    else:
                        xpath = f'//*[@id="__layout"]/div/div[2]/div[1]/main/section/div[3]/div[3]/div[{i - 12}]/a'

                    # Получаем ссылку на игру
                    element = driver.find_element(By.XPATH, xpath)
                    game_link = element.get_attribute("href")
                    print(f"Ссылка на игру {i}: {game_link}")

                    # Открываем ссылку в новой вкладке
                    driver.execute_script("window.open(arguments[0], '_blank');", game_link)

                    # Переключаемся на новую вкладку
                    driver.switch_to.window(driver.window_handles[1])

                    # Задержка для загрузки страницы
                    time.sleep(random.uniform(2, 4))

                    # Парсим данные игры
                    try:
                        game_name = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div[1]/div[1]/div/div/div[2]/div[3]/div[1]/h1').text
                        metascore = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div[1]/div[1]/div/div/div[2]/div[3]/div[4]/div[1]/div/div[1]/div[2]/div/div/span').text
                        user_score = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/div[1]/div[1]/div/div/div[2]/div[3]/div[4]/div[2]/div[1]/div[2]/div/div/span').text

                        print(f"Название игры: {game_name}")
                        print(f"Metascore: {metascore}")
                        print(f"User Score: {user_score}")
                    except Exception as e:
                        print(f"Ошибка при извлечении данных: {e}")

                    # Закрываем вкладку и возвращаемся на основную страницу
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    # Симуляция действий пользователя (движение мыши, прокрутка)
                    simulate_user_actions(driver)

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

