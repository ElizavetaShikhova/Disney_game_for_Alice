import json
from random import choice
import requests
import sqlite3
from make_logs import log_to_file


def choose_level(modes,user):
    for _ in range(7):
        n = choose_film(modes,user)
        if isinstance(n, str):
            return n
        film = get_film(n)
        if not film:
            return

        con = sqlite3.connect('/home/minoorr/alisa2/translation.db')
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
        try:
            return {'film':name_of_film[0][0],'id':int(film['_id']),'name':name_of_character[0][0],'image':image[0][0]}
        except Exception as e:
            error = f'name of error: {e}, name of film: "{name_of_film}", id:{film["_id"]}, name of character: "{name_of_character}", image: {image}'
            pass
    log_to_file(error)
    return



def choose_film(modes, user):
    categories = modes[user]['categories']
    with open('/home/minoorr/alisa2/users.json') as f:
        played = json.load(f)[user]['played']
    with open('/home/minoorr/alisa2/numbers.json') as f:
        f = json.load(f)

    try:
        numbers = f["number_for_random_choosing"][categories]
    except Exception:
        numbers = f["number_for_random_choosing"]['tvShows'] + f["number_for_random_choosing"]['films'] + \
                  f["number_for_random_choosing"]['shortFilms']

    if set(numbers) &set(played)==set(numbers):
        return 'Ты уже угадывал все фильмы из этой категории'

    while True:
        num = choice(numbers)#set(numbers)-set(played) и без while True
        if int(num) not in played:
            break
    return num

def get_film(n):
    search_api_server = f"https://api.disneyapi.dev/characters/{n}"
    response = requests.get(search_api_server)
    if not response:
        log_to_file(f'{search_api_server} did not respond')
        pass
    return response.json()
