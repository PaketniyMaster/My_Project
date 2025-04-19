import csv

file_path = r'D:\VSC Projects\App\Project\app\csv\reviews_10K-15k.csv'


titles = set()

with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        titles.add(row['game_title'])

print(f'Уникальных game_title: {len(titles)}')