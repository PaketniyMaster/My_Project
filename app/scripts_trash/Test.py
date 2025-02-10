from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def parse_reviews_from_row(row_element):
    reviews = []
    try:
        # Найти только основные блоки отзывов в строке
        review_elements = row_element.find_elements(By.XPATH, './/div[@class="apphub_CardContentMain"]')
        for review_element in review_elements:
            try:
                # Получить основной текст отзыва
                review_text = review_element.text.strip()
                if review_text and review_text not in reviews:  # Убедиться, что отзыв уникален
                    reviews.append(review_text)
            except Exception as e:
                print(f"Ошибка при извлечении текста отзыва: {e}")
    except Exception as e:
        print(f"Ошибка при обработке строки с отзывами: {e}")
    return reviews

def parse_page_reviews(driver, page_number):
    reviews = []
    try:
        # Найти строки с отзывами для текущей страницы
        row_elements = driver.find_elements(By.XPATH, f'//div[contains(@id, "page_{page_number}_row")]')
        print(f"Найдено строк на странице {page_number}: {len(row_elements)}")
        for row in row_elements:
            reviews += parse_reviews_from_row(row)
    except Exception as e:
        print(f"Ошибка при парсинге страницы {page_number}: {e}")
    return reviews

def scroll_to_next_page(driver, current_page):
    try:
        # Определяем XPath следующей страницы
        next_page_xpath = f'//*[@id="page{current_page + 1}"]'
        driver.execute_script("window.scrollBy(0, 1000);")  # Пролистывание вниз
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, next_page_xpath)))
        print(f"Найдена следующая страница: {current_page + 1}")
        return True
    except Exception as e:
        print(f"Ошибка при пролистывании: {e}")
        return False

def main():
    url = "https://steamcommunity.com/app/1307580/reviews/?browsefilter=trendsixmonths&snr=1_5_100010_&p=1"
    driver = webdriver.Chrome()
    driver.get(url)
    
    all_reviews = []
    current_page = 1
    max_pages = 3

    try:
        while current_page <= max_pages:
            print(f"Парсинг страницы {current_page}")
            # Парсинг отзывов на текущей странице
            page_reviews = parse_page_reviews(driver, current_page)
            print(f"Извлеченные отзывы с страницы {current_page}: {len(page_reviews)}")
            all_reviews += page_reviews
            
            # Переход к следующей странице
            if scroll_to_next_page(driver, current_page):
                current_page += 1
            else:
                break

    except Exception as e:
        print(f"Общая ошибка: {e}")
    finally:
        driver.quit()

    # Удаляем дубликаты отзывов
    unique_reviews = list(set(all_reviews))

    print(f"Всего извлечено уникальных отзывов: {len(unique_reviews)}")
    for review in unique_reviews:
        print(review)

if __name__ == "__main__":
    main()
