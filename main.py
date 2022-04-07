from flask import Flask, request
import sys
import json
import os
# sys.path.insert(1,'/home/minoorr/alisa2/working_with_api')
from working_with_api import choose_level

app = Flask(__name__)
file_name = '/home/minoorr/alisa2/users.json'
modes = {}


@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False,
            'text': ''
        }
    }

    handle_dialog(response, request.json)

    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    with open(file_name) as f:
        data = json.load(f)
    if req['session']['new']:
        if user_id in modes:
            del modes[user_id]
        if user_id not in data.keys():
            res['response']['text'] = \
                'Привет! Как хорошо ты знаешь фильмы disney? Давай проверим! Но для начала нужно познакомиться. Как тебя зовут?'
            data[user_id] = {'name': None, 'played': [], 'guessed': [], 'points':0}
            save_the_progress(data, file_name)
            return
        else:
            res['response'][
                'text'] = f"Я рада, что ты здесь, {data[user_id]['name'].title()}. Выбирай режим игры. Ты можешь угадывать: " \
                          f"1)название фильма/мультфильма/тв сериала по фотаграфии героя и его имени" \
                          f" или 2)угадывать имя героя по фотографии героя и названию фильма"
            res['response']['buttons'] = [{
                'title': '1',
                'hide': True},
                {'title': '2',
                 'hide': True}]
            return

    if data[user_id]['name'] is None:
        first_name = get_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            data[user_id]['name'] = first_name

            save_the_progress(data,file_name)

            res['response'][
                'text'] = f'Приятно познакомиться, {first_name.title()}. Выбирай режим игры. Ты можешь угадывать: 1)название фильма/мультфильма/тв сериала по фотаграфии героя и его имени или 2)угадывать имя героя по фотографии героя и названию фильма'
            res['response']['buttons'] = [{
                'title': '1',
                'hide': True},
                {'title': '2',
                 'hide': True}]
            return

    if user_id not in modes:  # Если игрок еще не выбрал режим игры
        if req['request']['command'] == '2':
            modes[user_id] = {'mode': 2, 'categories': None, 'attempt': 0,'hint':0}
        elif req['request']['command'] == '1':
            modes[user_id] = {'mode': 1, 'categories': None, 'attempt': 0,'hint':0}
        else:
            res['response']['text'] = 'Прости, я тебя не поняла. Так что ты выбераешь?'
            res['response']['buttons'] = [{
                'title': '1',
                'hide': True},
                {'title': '2',
                 'hide': True}]
            return
        res['response']['text'] = 'Теперь выбери категорию. Фильмы, короткие фильмы или тв сериалы?'
        res['response']['buttons'] = [{
            'title': 'Фильмы',
            'hide': True},
            {'title': 'Короткие фильмы',
             'hide': True},
            {'title': 'Тв сериалы',
             'hide': True},
            {'title': 'Все вместе',
             'hide': True}]
        return

    if user_id in modes and modes[user_id]['categories'] is None:  # Если игрок еще не выбрал категорию
        if 'коротк' in req['request']['command']:
            modes[user_id]['categories'] = 'shortFilms'
        elif 'сериал' in req['request']['command']:
            modes[user_id]['categories'] = 'tvShows'
        elif 'фильм' in req['request']['command']:
            modes[user_id]['categories'] = 'films'
        elif 'все' in req['request']['command'] or 'всё' in req['request']['command']:
            modes[user_id]['categories'] = 'all'
        else:
            res['response']['text'] = 'Извини, я тебя не поняла. Какую категорию выберем?'
            res['response']['buttons'] = [{
                'title': 'Фильмы',
                'hide': True},
                {'title': 'Короткие фильмы',
                 'hide': True},
                {'title': 'Тв сериалы',
                 'hide': True},
                {'title': 'Все вместе',
                 'hide': True}]
            return

    if user_id in modes and modes[user_id]['attempt']:
        guessed = False
        if req['request']['command'] == 'сдаюсь':
            res['response']['text'] = f'Очень жаль, это был фильм "{modes[user_id]["ans"]}". '
            modes[user_id]['attempt'] = 0 #сброс  в  отдльной  функции?
            modes[user_id]['hint'] = 0
            guessed=True
        elif req['request']['command'] == 'подсказка':

            hint=get_hint(user_id)

            if not hint:
                res['response']['text'] = f'У тебя больше не осталось подсказок!'
                res['response']['buttons'] = [{
                    'title': 'Сдаюсь',
                    'hide': True},
                    {'title': 'Подсказка',
                     'hide': True}]
                return
            res['response']['text'] = f'Вот несколько букв из названия фильма: "{hint}...". Но помни, чем больше подсказок, тем меньше баллов!'
            #modes[user_id]['attempt'] += 1
            res['response']['buttons'] = [{
                'title': 'Сдаюсь',
                'hide': True},
                {'title': 'Подсказка',
                 'hide': True}]
            return
        for word in preparing_the_answer(modes[user_id]['ans']):
            if req['request']['command'] == word:
                res['response'][
                    'text'] = f"Верно! Ты угадал с {modes[user_id]['attempt']} попытки и заработал ... Поехали дальше. "  # посчитать баллы и сохранить
                modes[user_id]['attempt'] = 0
                modes[user_id]['hint'] = 0

                data[user_id]['guessed'].append(data[user_id]['played'][-1])
                data = count_the_points(user_id,modes,data)

                save_the_progress(data,file_name)

                guessed = True
        if not guessed:
            res['response']['text'] = 'Попробуй еще раз'
            modes[user_id]['attempt'] += 1
            res['response']['buttons'] = [{
                'title': 'Сдаюсь',
                'hide': True},
                {'title': 'Подсказка',
                 'hide': True}]
            return

    if user_id in modes and modes[user_id]['categories'] and not modes[user_id]['attempt']:
        res_dict = choose_level(modes, user_id)
        if isinstance(res_dict, str):
            res['response']['text'] = res_dict
            res['response']['buttons'] = [{
                'title': 'Фильмы',
                'hide': True},
                {'title': 'Короткие фильмы',
                 'hide': True},
                {'title': 'Тв сериалы',
                 'hide': True},
                {'title': 'Все вместе',
                 'hide': True}]
            return

        modes[user_id]['attempt'] += 1
        data[user_id]['played'].append(res_dict['id'])
        with open(file_name, 'w') as f:  # Может, стоит записать после угадывания? Завести функцию с сохранением
            json.dump(data, f)
        res['response'][
            'text'] += f"Угадай фильм по герою! Герой - {res_dict['name'].split('/')[0]}. В названии фильма {len(preparing_the_answer(res_dict['film'])[0].split())} слов(а)"
        res['response']['card'] = {}
        res['response']['card']['image_id'] = res_dict['image']
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = res['response']['text']

        modes[user_id]['ans'] = res_dict['film']
        return

def get_hint (user_id):
    if modes[user_id]['hint'] <3:
        modes[user_id]['hint']+=1
        return modes[user_id]['ans'][:modes[user_id]['hint']]
    return 0

def get_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


def preparing_the_answer(name_of_the_film):
    ans = name_of_the_film.lower().split('/')
    a = []
    for i in ans:
        res = ''
        if set(list(i)) & {'-', '!', '?', ','}:
            for j in list(i):
                if j not in {'-', '!', '?', ','}:
                    res += j
                else:
                    res+=' '
        a.append(' '.join(res.split()))
    if a[0]:
        return a + ans
    else:
        return ans

def count_the_points(user_id,modes,data):
    with open('/home/minoorr/alisa2/points.json') as f:
        points = json.load(f)
    data[user_id]['points'] += points['points'][f"{modes[user_id]['hint']} hint"]
    return data

def save_the_progress(data,file_name):
    with open(file_name, 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8030))
    app.run(host='0.0.0.0', port=port)
