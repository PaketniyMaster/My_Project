from app.config import settings
from app.Parsing.Driver import setup_driver  # Импортируем setup_driver из отдельного файла
from app.Parsing.Games_list import get_games_list  # Импортируем функцию парсинга игр
#from app.Parsing.Game_details import parse_games_multithreaded
#from app.Parsing.Parse_review import parse_all_reviews
from app.Parsing.Game_details_bs4 import parse_games_multithreaded
from app.Parsing.parse_review_bs4 import parse_steam_reviews
#from app.Parsing.Game_details_bs4 import SteamParser

if __name__ == "__main__":
    steam_url = settings.STEAM_URL  # URL страницы поиска игр
    #driver = setup_driver()

    try:
        #parse_all_reviews(driver)
        #parse_games_multithreaded()
        #get_games_list(driver, steam_url)  # Парсим 10 игр
        #parse_games_multithreaded()
        parse_steam_reviews()
        
        
        #excluded_tags = [492, 872, 44868, 12095, 21978, 856791, 9130, 24904, 10397, 13906, 5577, 1445]
        #parser = SteamParser("gamesbs4.csv", excluded_tags)
        #parser.fetch_games()
    finally:
        #driver.quit()
        print("FINISH")
