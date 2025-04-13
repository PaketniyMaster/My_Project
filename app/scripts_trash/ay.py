import requests
from bs4 import BeautifulSoup

url = "https://www.russianfood.com/recipes/bytype/?fid=3&page=1"
headers = {"User-Agent": "Mozilla/5.0"}

res = requests.get(url, headers=headers)
res.encoding = 'windows-1251'
soup = BeautifulSoup(res.text, "html.parser")

# Попробуем вывести ВСЕ ссылки
for a in soup.find_all("a"):
    href = a.get("href")
    if href and "/recipes/recipe.php" in href:
        print(href)
