from app.config import settings
from app.Parsing.Driver import setup_driver  # Импортируем setup_driver из отдельного файла
from app.Parsing.Games_list import get_games_list  # Импортируем функцию парсинга игр
from app.Parsing.Game_details import parse_games_multithreaded
from app.Parsing.Parse_review import parse_all_reviews

if __name__ == "__main__":
    steam_url = settings.STEAM_URL  # URL страницы поиска игр
    driver = setup_driver()

    try:
        #parse_all_reviews(driver)
        parse_games_multithreaded()
        #get_games_list(driver, steam_url)  # Парсим 10 игр
    finally:
        driver.quit()
