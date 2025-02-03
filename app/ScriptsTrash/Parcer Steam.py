from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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
    service = Service('D:\VSC Projects\WebDriver\chromedriver-win64\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver

def get_elements(driver, url, start_index, end_index):
    driver.get(url)
    print(f"Открыта страница: {url}")

    found = 0
    current_index = start_index
    while found < (end_index - start_index + 1):
        css_selector = f"#search_resultsRows > a:nth-child({current_index}) > div.responsive_search_name_combined > div.col.search_name.ellipsis > span"
        #search_resultsRows > a:nth-child(1)
        #search_resultsRows > a:nth-child(2)
        elements = driver.find_elements(By.CSS_SELECTOR, css_selector)

        if elements:
            print(f"Элемент {current_index}: {elements[0].text}")
            found += 1
            current_index += 1
        else:
            # Прокручиваем страницу, но ищем тот же элемент снова
            print(f"Элемент {current_index} не найден, прокручиваем страницу...")
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(random.uniform(2, 5))  # Задержка перед повторной попыткой поиска
            # Не увеличиваем current_index, чтобы повторно искать тот же элемент



if __name__ == "__main__":
    steam_url = "https://store.steampowered.com/search/?sort_by=Released_DESC&untags=492%2C872%2C44868%2C12095%2C21978%2C856791%2C9130%2C24904%2C10397%2C13906%2C5577%2C1445&category1=998&hidef2p=1&ndl=1"
    driver = setup_driver()

    try:
        get_elements(driver, steam_url, 1, 500)
    finally:
        # Браузер не будет закрываться до тех пор, пока не будут найдены все элементы
        print("Парсинг завершен, браузер остается открытым для дальнейшей работы.")
