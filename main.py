from flask import Flask, request
import json
import os

from working_with_api import choose_level
from leader_board import create_leader_board

app = Flask(__name__)
file_name = '/home/minoorr/alisa2/users.json'
modes = {}
with open('/home/minoorr/alisa2/numbers.json') as f:
    numbers = json.load(f)

with open('/home/minoorr/alisa2/phrases.json') as f:
    phrases = json.load(f)

LANG = 'Russian'


@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False,
            'text': '',
            'buttons': []
        }
    }

    handle_dialog(response, request.json)

    return json.dumps(response)


def start(user_id, data, res):
    if not data or user_id not in data.keys():
        res['response']['text'] = phrases['phrases'][LANG]['welcome and ask name']
        data[user_id] = {'name': None, 'played': [], 'guessed': [], 'points': 0}
        save_the_progress(data, file_name)
        return res, data
    else:
        res['response']['text'] = eval(f'f"{phrases["phrases"][LANG]["welcome and choose mode"]}"')
        res['response']['buttons'] = [{
            'title': phrases["buttons"][LANG]["leaderboard"],
            'hide': True},
            {'title': '1',
             'hide': True},
            {'title': '2',
             'hide': True}]
        return res, data


def ask_name(user_id, res, data, req):
    first_name = get_name(req)
    if first_name is None:
        res['response']['text'] = phrases['phrases'][LANG]["didn't hear name"]
    else:
        data[user_id]['name'] = first_name

        save_the_progress(data, file_name)

        res['response']['text'] = eval(f'f"{phrases["phrases"][LANG]["glad to meet you"]}"')
        res['response']['buttons'] += [{
            'title': '1',
            'hide': True},
            {'title': '2',
             'hide': True}]
    return res, data


def choose_mode(user_id, res, req):
    if user_id not in modes or not modes[user_id]['mode']:  # Если игрок еще не выбрал режим игры
        if req['request']['command'] == '2':
            modes[user_id] = {'mode': 2, 'categories': None, 'attempt': 0, 'hint': 0}
        elif req['request']['command'] == '1':
            modes[user_id] = {'mode': 1, 'categories': None, 'attempt': 0, 'hint': 0}
        else:
            res['response']['text'] = phrases["phrases"][LANG]["did not get"]
            res['response']['buttons'] += [{
                'title': '1',
                'hide': True},
                {'title': '2',
                 'hide': True}]
            return res
        res['response']['text'] = phrases["phrases"][LANG]["choose categories"]
        res['response']['buttons'] = [{
            'title': phrases["buttons"][LANG]["films"],
            'hide': True},
            {'title': phrases["buttons"][LANG]["short films"],
             'hide': True},
            {'title': phrases["buttons"][LANG]["TV series"],
             'hide': True},
            {'title': phrases["buttons"][LANG]["all"],
             'hide': True}]
        return res


def choose_categories(user_id, res, req):
    if (phrases["buttons"][LANG]["short films"]).lower() in req['request']['command']:
        modes[user_id]['categories'] = 'shortFilms'
    elif (phrases["buttons"][LANG]["TV series"]).lower() in req['request']['command']:
        modes[user_id]['categories'] = 'tvShows'
    elif (phrases["buttons"][LANG]["films"]).lower() in req['request']['command']:
        modes[user_id]['categories'] = 'films'
    elif 'все' in req['request']['command'] or 'всё' in req['request']['command']:
        modes[user_id]['categories'] = 'all'
    else:
        res['response']['text'] = phrases["phrases"][LANG]["did not get"]
        res['response']['buttons'] = [{
            'title': phrases["buttons"][LANG]["films"],
            'hide': True},
            {'title': phrases["buttons"][LANG]["short films"],
             'hide': True},
            {'title': phrases["buttons"][LANG]["TV series"],
             'hide': True},
            {'title': phrases["buttons"][LANG]["all"],
             'hide': True}]
        return res


def game(user_id, res, req, data, mode):
    res['response']['buttons'] += [{'title': phrases["buttons"][LANG]["change category"], 'hide': True},
                                   {'title': phrases["buttons"][LANG]["change mode"], 'hide': True}]
    if req['request']['command'] == (phrases["buttons"][LANG]["change mode"]).lower():
        res['response']['text'] = phrases["phrases"][LANG]["change the mode"]
        res['response']['buttons'] = [{
            'title': '1',
            'hide': True},
            {'title': '2',
             'hide': True}]
        modes[user_id]['categories'] = None
        modes[user_id]['mode'] = None
        modes[user_id]['attempt'] = 0
        modes[user_id]['hint'] = 0
        return res, data
    if req['request']['command'] == (phrases["buttons"][LANG]["change category"]).lower():
        res['response']['text'] = phrases["phrases"][LANG]["change the category"]
        res['response']['buttons'] = [{
            'title': phrases["buttons"][LANG]["films"],
            'hide': True},
            {'title': phrases["buttons"][LANG]["short films"],
             'hide': True},
            {'title': phrases["buttons"][LANG]["TV series"],
             'hide': True},
            {'title': phrases["buttons"][LANG]["all"],
             'hide': True}]
        modes[user_id]['categories'] = None
        modes[user_id]['attempt'] = 0
        modes[user_id]['hint'] = 0
        return res, data

    if user_id in modes and modes[user_id]['attempt']:
        guessed = False
        if req['request']['command'] == (phrases["buttons"][LANG]["give up"]).lower():
            res['response']['text'] = eval(f"f'{phrases['phrases'][LANG]['the player did not guessed']}'")
            modes[user_id]['attempt'] = 0
            modes[user_id]['hint'] = 0
            guessed = True
        elif req['request']['command'] == (phrases["buttons"][LANG]["hint"]).lower():

            hint = get_hint(user_id)

            if not hint:
                res['response']['text'] = phrases["phrases"][LANG]["no more hints"]
                res['response']['buttons'] += [{
                    'title': phrases["buttons"][LANG]["give up"],
                    'hide': True},
                    {'title': phrases["buttons"][LANG]["hint"],
                     'hide': True}]
                return res, data
            if mode == 1:
                res['response']['text'] = eval(f"f'{phrases['phrases'][LANG]['hint for mode 1']}'")
            else:
                res['response'][
                    'text'] = eval(f"f'{phrases['phrases'][LANG]['hint for mode 2']}'")
            # modes[user_id]['attempt'] += 1
            res['response']['buttons'] += [{
                'title': phrases["buttons"][LANG]["give up"],
                'hide': True},
                {'title': phrases["buttons"][LANG]["hint"],
                 'hide': True}]
            return res, data
        for word in preparing_the_answer(modes[user_id]['ans']):
            if preparing_the_answer(req['request']['command'])[0] == word:
                data, points = count_the_points(user_id, data)
                res['response']['text'] = eval(f'f"{phrases["phrases"][LANG]["guessed right"]}"')
                modes[user_id]['attempt'] = 0
                modes[user_id]['hint'] = 0

                data[user_id]['guessed'].append(data[user_id]['played'][-1])

                save_the_progress(data, file_name)

                guessed = True
        if not guessed:
            res['response']['text'] = eval(f'f"{phrases["phrases"][LANG]["try again"]}"')
            modes[user_id]['attempt'] += 1
            res['response']['buttons'] = [{
                'title': phrases["buttons"][LANG]["give up"],
                'hide': True},
                                             {'title': phrases["buttons"][LANG]["hint"],
                                              'hide': True}] + res['response']['buttons']
            return res, data
    if user_id in modes and modes[user_id]['categories'] and not modes[user_id]['attempt']:
        res_dict = choose_level(modes, user_id, data[user_id]['played'], numbers, phrases, LANG)
        if not res_dict:
            res['response']['text'] = phrases["phrases"][LANG]["oops"]
            return res, data
        if isinstance(res_dict, str):
            res['response']['text'] += res_dict
            modes[user_id]['categories'] = None
            res['response']['buttons'] = [{
                'title': phrases["buttons"][LANG]["films"],
                'hide': True},
                {'title': phrases["buttons"][LANG]["short films"],
                 'hide': True},
                {'title': phrases["buttons"][LANG]["TV series"],
                 'hide': True},
                {'title': phrases["buttons"][LANG]["all"],
                 'hide': True}]
            return res, data

        modes[user_id]['attempt'] += 1
        data[user_id]['played'].append(res_dict['id'])
        save_the_progress(data, file_name)
        if mode == 1:
            res['response'][
                'text'] += eval(f'f"{phrases["phrases"][LANG]["the hero is"]}"')
        else:
            res['response'][
                'text'] += eval(f'f"{phrases["phrases"][LANG]["the film is"]}"')
        res['response']['card'] = {}
        res['response']['card']['image_id'] = res_dict['image']
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = res['response']['text']
        if mode == 1:
            modes[user_id]['ans'] = res_dict['film']
        else:
            modes[user_id]['ans'] = res_dict['name']
        return res, data
    return res, data


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    with open(file_name) as f:
        data = json.load(f)

    if req['session']['new']:
        if user_id in modes:
            del modes[user_id]
        res, data = start(user_id, data, res)
        return
    elif data[user_id]['name']:
        res['response']['buttons'] = [{
            'title': phrases["buttons"][LANG]["leaderboard"],
            'hide': True}]

    if data[user_id]['name'] is None:
        res, data = ask_name(user_id, res, data, req)
        return

    if req['request']['command'] == (phrases["buttons"][LANG]["leaderboard"]).lower():
        res['response']['text'] = create_leader_board(data, user_id)
        return

    if user_id not in modes or not modes[user_id]['mode']:  # Если игрок еще не выбрал режим игры
        res = choose_mode(user_id, res, req)
        return

    if modes[user_id]['categories'] is None:  # Если игрок еще не выбрал категорию
        r = choose_categories(user_id, res, req)
        if r:
            res = r
            return
    res, data = game(user_id, res, req, data, modes[user_id]['mode'])


def get_hint(user_id):
    if modes[user_id]['hint'] < 3:
        modes[user_id]['hint'] += 1
        return modes[user_id]['ans'][:modes[user_id]['hint']]
    return 0


def get_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


def preparing_the_answer(name_of_the_film):
    ans = name_of_the_film.lower().split('/')
    a = []
    if LANG == 'Russian':
        for i in ans:
            res = ''
            for j in i:
                if j not in {'-', '!', '?', ',', ':'}:
                    if not res or res[-1] != j:
                        if j == 'ё':
                            res += 'е'
                        else:
                            res += j
                elif res[-1] != ' ':
                    res += ' '
            a.append(res)
    else:
        pass
    return a


def count_the_points(user_id, data):
    with open('/home/minoorr/alisa2/points.json') as f:
        points = json.load(f)
    if points['points'][f"{modes[user_id]['hint']} hint"] - modes[user_id]['attempt'] + 1 <= 0:
        p = 1
    else:
        p = points['points'][f"{modes[user_id]['hint']} hint"] - modes[user_id]['attempt'] + 1
    data[user_id]['points'] += p
    return data, p


def save_the_progress(data, file_name):
    with open(file_name, 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8030))
    app.run(host='0.0.0.0', port=port)
