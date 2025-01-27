from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

# Инициализация WebDriver с использованием Service
service = Service('D:/VSC Projects/WebDriver/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service=service)

# Открываем нужную ссылку
url = "https://store.steampowered.com/app/1307580/TOEM_A_Photo_Adventure/"
driver.get(url)

# Ожидаем загрузки страницы
time.sleep(5)

# Используем уточненный XPath, чтобы выбрать второй элемент с нужным классом
tooltip_text = driver.find_element(By.XPATH, '//*[@class="user_reviews_summary_row"][2]')
tooltip_data = tooltip_text.get_attribute('data-tooltip-html')

print(tooltip_data)

# Закрываем браузер
driver.quit()
