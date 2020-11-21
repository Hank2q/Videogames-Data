import sqlite3
import json
from datetime import datetime, date


def parse_date(date_string):
    try:
        release_date = datetime.strptime(date_string, '%b %d, %Y')
    except ValueError:
        return None
    return date.strftime(release_date, '%Y-%m-%d')


open('../data/vg.db', 'w').close()
db = sqlite3.connect('../data/vg.db')
cursor = db.cursor()
for line in open('commands.txt'):
    with db:
        cursor.execute(line)
ps4 = json.load(open('../data/ps4.json'))
pc = json.load(open('../data/pc.json'))
xbox = json.load(open('../data/xboxone.json'))
switch = json.load(open('../data/switch.json'))
all_ratings = set()
all_genres = set()
all_developers = set()
platforms = {'Pc': pc, 'Ps4': ps4, 'Xbox one': xbox, 'Switch': switch}

for platform_name, platform_data in platforms.items():
    with db:
        cursor.execute('INSERT INTO platforms(name) VALUES(?)',
                       (platform_name,))
    for entry in platform_data:
        title, info = list(entry.items())[0]
        if info:
            developer = info['developer']
            rating = info['rating']
            genres = info['genres']
            all_ratings.add(rating)
            all_developers.add(developer)
            for genre in genres:
                all_genres.add(genre)
print('[TABLE: platforms FILLED]')


extract = [all_developers, all_ratings, all_genres]
for table_name, data in zip(['developers', 'ratings', 'genres'], extract):
    data = list(filter(None, data))
    for entry in data:
        with db:
            cursor.execute(
                f'INSERT INTO {table_name}(name) VALUES(?)', (entry,))
    print(f'[TABLE: {table_name} FILLED]')

game_id = 1
for platform_name, platform_data in platforms.items():
    for entry in platform_data:
        title, info = list(entry.items())[0]
        if not info:
            continue
        user_score = info['user score']
        meta_score = info['meta score']
        developer = info['developer']
        release_date = parse_date(info['release date'])
        rating = info['rating']
        genres = info['genres']

        rating_id = cursor.execute(
            'SELECT id FROM ratings WHERE name=?', (rating,)).fetchone()

        if rating_id:
            rating_id = rating_id[0]

        developer_id = cursor.execute(
            'SELECT id FROM developers WHERE name=?', (developer,)).fetchone()
        if developer_id:
            developer_id = developer_id[0]

        platform_id = cursor.execute(
            'SELECT id FROM platforms WHERE name=?', (platform_name,)).fetchone()[0]

        with db:
            cursor.execute('INSERT INTO games(id, title, meta_score, user_score, release_date, platform_id, developer_id, rating_id) VALUES(?,?,?,?,?,?,?,?)',
                           (game_id, title, meta_score, user_score, release_date, platform_id, developer_id, rating_id))
        print(f'[GAME: {title} ADDED]')
        if genres:
            for genre in set(genres):
                genre_id = cursor.execute(
                    'SELECT id FROM genres WHERE name=?', (genre,)).fetchone()[0]
                with db:
                    cursor.execute(
                        'INSERT INTO game_genre(game_id, genre_id) VALUES(?,?)',
                        (game_id, genre_id))
        game_id += 1
print('[TABLE: games FILLED]')
