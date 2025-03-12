import pandas as pd

# Загрузка CSV
input_file = "reviews_test1.csv"  # Замените на ваш файл
output_file = "filtered.csv"

# Чтение данных
df = pd.read_csv(input_file, delimiter=";")

# Фильтрация
filtered_df = df[df["game_title"] == "Jagged Alliance 3"]

# Сохранение
filtered_df.to_csv(output_file, index=False, sep=";")

print(f"Фильтрованные данные сохранены в {output_file}")
