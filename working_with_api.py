import json
from random import choice
import requests
import sqlite3


def choose_level(modes,user):
    n = choose_film(modes,user)
    if isinstance(n, str):
        return n
    film = get_film(n)
    mode = modes[user]['mode']
    con = sqlite3.connect('/home/minoorr/alisa2/translation.db')                                            #работу с бд перенеси в др функцию
    cur = con.cursor()
    if film['films']:
        genre = 'films'
    elif film['tvShows']:
        genre = 'tvShows'
    else:
        genre = 'shortFilms'
    name_of_character = cur.execute("""SELECT translated_name FROM names where eng_name==?""",(film['name'],)).fetchall()
    name_of_film = cur.execute("""SELECT translated_films FROM films where eng_films==?""",(film[genre][0],)).fetchall()
    image = cur.execute("""SELECT image FROM names where eng_name==?""",(film['name'],)).fetchall()
    if mode == 1:
        return {'film':name_of_film[0][0],'id':int(film['_id']),'name':name_of_character[0][0],'image':image[0][0]}
    if mode==2:                 #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        pass


def choose_film(modes, user):
    categories = modes[user]['categories']
    with open('/home/minoorr/alisa2/users.json') as f:
        played = json.load(f)[user]['played']
    with open('/home/minoorr/alisa2/numbers.json') as f:
        f = json.load(f)
    try:
        numbers = f["number_for_random_choosing"][categories]
        if set(f["number_for_random_choosing"][categories]) & set(played) == set(
                f["number_for_random_choosing"][categories]):
            return 'Ты уже угадывал все фильмы из этой категории'
    except Exception:
        numbers = f["number_for_random_choosing"]['tvShows'] + f["number_for_random_choosing"]['films'] + \
                  f["number_for_random_choosing"]['shortFilms']

    while True:
        num = choice(numbers)
        if int(num) not in played:
            break
    return num

def get_film(n):
    search_api_server = f"https://api.disneyapi.dev/characters/{n}"
    response = requests.get(search_api_server)
    if not response:
        pass
    return response.json()

