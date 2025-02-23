from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import random

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    prefs = {
        "profile.default_content_setting_values": {
            "images": 2,  # Блокируем изображения
            "stylesheet": 2,  # Блокируем CSS
            "font": 2,  # Блокируем шрифты
            "plugins": 2,  # Блокируем плагины (например, Flash)
            "video": 2,  # Отключаем видео
        },
        "profile.managed_default_content_settings": {
            "images": 2,
            "media_stream": 2,  # Блокируем доступ к веб-камере и микрофону
        },
        "profile.default_content_setting_values.automatic_downloads": 2  # Блокируем автозагрузки
    }
    
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.page_load_strategy = "eager"  # Ждёт только DOMContentLoaded, а не всю страницу
    # Отключаем автозапуск видео (важно для Steam!)
    #chrome_options.add_argument("--autoplay-policy=user-required")

    # Случайный User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    service = Service('D:\\VSC Projects\\WebDriver\\chromedriver-win64\\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver
