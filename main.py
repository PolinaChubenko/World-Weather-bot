from dotenv import load_dotenv
import os
from os.path import join, dirname
from googletrans import Translator
import country_converter as coco
from flask import Flask, request
import json
import requests
from src import texts, urls
import re

translator = Translator()
app = Flask(__name__)
users = dict()


def get_from_env(key):
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key)


def send_message(chat_id, text, parse_mode=None, reply_markup=None):
    method = "sendMessage"
    token = get_from_env("BOT_TOKEN")
    url = urls.TELEGRAM_BOT_URL + f"{token}/{method}"
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "reply_markup": reply_markup}
    requests.post(url, data=data)


def send_dice(chat_id, reply_markup):
    method = "sendDice"
    token = get_from_env("BOT_TOKEN")
    url = urls.TELEGRAM_BOT_URL + f"{token}/{method}"
    url = urls.TELEGRAM_BOT_URL + f"{token}/{method}"
    data = {"chat_id": chat_id, "reply_markup": reply_markup}
    requests.post(url, data=data)


def send_location(chat_id, lon, lat):
    method = "sendLocation"
    token = get_from_env("BOT_TOKEN")
    url = urls.TELEGRAM_BOT_URL + f"{token}/{method}"
    data = {"chat_id": chat_id, "latitude": lat, "longitude": lon}
    requests.post(url, data=data)


def logging(data, filename="log.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_coord_for_city(city):
    url = urls.API_GEOCODING_URL
    param_request = {'q': city, 'limit': urls.LIMIT, 'appid': get_from_env("API_KEY")}
    response = requests.get(url, params=param_request)
    return response


def get_response_for_city(city, url):
    param_request = {'q': city, 'appid': get_from_env("API_KEY"), 'lang': 'ru', 'cnt': 1, 'units': 'metric'}
    response = requests.get(url, params=param_request)
    return response


def get_response_for_coord(lat, lon, url):
    param_request = {'lat': lat, 'lon': lon, 'appid': get_from_env("API_KEY"), 'lang': 'ru',
                     'cnt': 1, 'units': 'metric'}
    response = requests.get(url, params=param_request)
    return response


def get_country(r, t):
    try:
        country = r.json()[t]['country']
        if country != '':
            return coco.convert(names=country, to='name_short')
    except KeyError:
        return None
    return None


def form_answer(place_en, country, degrees, description, when, feels_like=0):
    sign = lambda i: ("+" if i > 0 else "") + str(i)
    answer = 'In ' + place_en
    if country is not None and country != place_en:
        answer += ' (' + country + ')'
    answer += ' is ' if when == "today" else ' will be '
    answer += sign(degrees) + ' degrees '
    answer += 'right now.' if when == "today" else 'tomorrow.'
    if when == "today":
        answer += ' Feels like ' + sign(feels_like) + ' degrees.'
    answer = re.sub('это ', '', translator.translate(answer, "ru").text)
    answer += " Сейчас на улице " if when == "today" else " Обещают, что на улице будет "
    answer += description + "."
    return answer


def form_keyboard(r):
    keyboard = {"inline_keyboard": []}
    for i in range(len(r.json())):
        coord = " (" + str(round(r.json()[i]['lat'])) + "°ш, " + str(round(r.json()[i]['lon'])) + '°д)'
        option = [{"text": translator.translate(get_country(r, i), "ru").text + coord,
                   "callback_data": str(r.json()[i]['lat']) + ' ' + str(r.json()[i]['lon'])}]
        keyboard["inline_keyboard"].append(option)
    return keyboard


def send_tomorrow_temperature(chat_id, place_en=None, lat=None, lon=None):
    if place_en is not None:
        response = get_response_for_city(place_en, urls.API_FORECAST_URL)
    else:
        response = get_response_for_coord(lat, lon, urls.API_FORECAST_URL)
    if response.status_code != 200:
        return send_message(chat_id, texts.no_answer)
    degrees = round(response.json()['list'][0]['main']['temp'])
    place_en = response.json()['city']['name']
    country = get_country(response, 'city')
    description = response.json()['list'][0]['weather'][0]['description']
    send_message(chat_id, form_answer(place_en, country, degrees, description, "tomorrow"))
    lon = response.json()['city']['coord']['lon']
    lat = response.json()['city']['coord']['lat']
    send_location(chat_id, lon, lat)


def send_today_temperature(chat_id, place_en=None, lat=None, lon=None):
    if place_en is not None:
        response = get_response_for_city(place_en, urls.API_BASE_URL)
    else:
        response = get_response_for_coord(lat, lon, urls.API_BASE_URL)
    if response.status_code != 200:
        return send_message(chat_id, texts.no_answer)
    degrees = round(response.json()['main']['temp'])
    feels_like = round(response.json()['main']['feels_like'])
    place_en = response.json()['name']
    country = get_country(response, 'sys')
    description = response.json()['weather'][0]['description']
    send_message(chat_id, form_answer(place_en, country, degrees, description, "today", feels_like))
    lon = response.json()['coord']['lon']
    lat = response.json()['coord']['lat']
    send_location(chat_id, lon, lat)


def get_place(chat_id, place, when):
    place_en = translator.translate(place, "en").text.title()
    print(place_en)
    coord = get_coord_for_city(place_en)
    if len(coord.json()) > 1:
        keyboard = form_keyboard(coord)
        return send_dice(chat_id, json.dumps(keyboard))
    if when == "today":
        return send_today_temperature(chat_id, place_en=place_en)
    return send_tomorrow_temperature(chat_id, place_en=place_en)


def start_command(chat_id):
    send_message(chat_id, texts.start_info)


def help_command(chat_id):
    contact_developer = json.dumps({'inline_keyboard': [[{
        "text": "Написать разработчику",
        "url": "telegram.me/penguiners"
    }]]})
    send_message(chat_id, texts.info, 'Markdown', contact_developer)


def is_command(r):
    try:
        if r.json["message"]["entities"][0]["type"] == "bot_command":
            return True
    except KeyError:
        return False
    return False


def is_callback_query(r):
    try:
        r.json["callback_query"]
    except KeyError:
        return False
    return True


def parse_callback_query(chat_id, data):
    lat, lon = data.split(' ')
    if users[chat_id] == "today":
        return send_today_temperature(chat_id, lat=lat, lon=lon)
    send_tomorrow_temperature(chat_id, lat=lat, lon=lon)


def parse_text(chat_id, text):
    if users[chat_id]:
        get_place(chat_id, text, users[chat_id])
    else:
        send_message(chat_id, texts.forgot)


def parse_command(chat_id, text):
    if text == "/start":
        start_command(chat_id)
    elif text == "/help":
        help_command(chat_id)
    elif text == "/today" or text == "/tomorrow":
        users[chat_id] = text[1:]
    else:
        send_message(chat_id, texts.do_not_know)


def get_chat_id(r):
    try:
        chat_id = r.json["message"]["chat"]["id"]
        return chat_id
    except KeyError:
        pass
    try:
        chat_id = r.json["callback_query"]["message"]["chat"]["id"]
        return chat_id
    except KeyError:
        pass
    return False


@app.route("/", methods=["POST"])
def processing():
    logging(request.json)

    chat_id = get_chat_id(request)
    if not chat_id:
        send_message(chat_id, texts.smth_wrong)
        return {"ok": True}

    if chat_id not in users.keys():
        users[chat_id] = ""

    if is_callback_query(request):
        parse_callback_query(chat_id, request.json["callback_query"]["data"])
    else:
        try:
            text = request.json["message"]["text"]
        except KeyError:
            send_message(chat_id, texts.do_not_understand)
            return {"ok": True}

        if is_command(request):
            parse_command(chat_id, text)
        else:
            parse_text(chat_id, text)

    print(users)
    return {"ok": True}


if __name__ == "__main__":
    app.run()
