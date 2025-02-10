import pandas as pd
import os

# Путь к файлу относительно текущей директории
file_path = os.path.join(os.path.dirname(__file__), 'reviews.csv')

# Чтение CSV файла
df = pd.read_csv(file_path)

# Подсчет уникальных значений в колонке 'game_title'
unique_game_titles = df.shape[0]

print(f'Количество уникальных game_title: {unique_game_titles}')
