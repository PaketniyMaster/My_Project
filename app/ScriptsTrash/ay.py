from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
