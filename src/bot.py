import json
import country_converter as coco
from flask import Flask, request
from googletrans import Translator
from src import emojis, texts, urls
from src.queries import logging
from src.queries import send_message, \
    send_location, send_dice
from src.queries import get_response_for_city_by_coord, \
    get_response_for_city_by_city, get_response_for_coord_by_city


translator = Translator()
app = Flask(__name__)
users = dict()


def get_country(r, t):
    try:
        country = r.json()[t]['country']
        if country != '':
            return coco.convert(names=country, to='name_short')
    except KeyError:
        return None
    return None


def form_answer(place_en, country, degrees, weather_id, description, when, feels_like=0):
    sign = lambda i: ("+" if i > 0 else "") + str(i)
    answer = 'In ' + place_en
    if country is not None and country != place_en:
        answer += ' (' + country + ')'
    print(answer)
    answer = translator.translate(answer, 'ru').text
    answer += ' сейчас ' if when == "today" else ' завтра будет '
    temp = translator.translate(sign(degrees) + ' degrees', 'ru').text
    answer += temp + ' по Цельсию '
    if when == "today":
        answer += '\nОщущается как ' + sign(feels_like) + '°C'
    answer += "\nСейчас в этом месте " if when == "today" else " Обещают, что завтра в этом месте будет "
    answer += description + emojis.get_emoji(weather_id)
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
        response = get_response_for_city_by_city(place_en, urls.API_FORECAST_URL)
    else:
        response = get_response_for_city_by_coord(lat, lon, urls.API_FORECAST_URL)
    if response.status_code != 200:
        return send_message(chat_id, texts.no_answer)
    weather_id = response.json()['list'][0]['weather'][0]['id']
    degrees = round(response.json()['list'][0]['main']['temp'])
    place_en = translator.translate(response.json()['city']['name'], dest="en").text.title()
    country = get_country(response, 'city')
    description = response.json()['list'][0]['weather'][0]['description']
    send_message(chat_id, form_answer(place_en, country, degrees, weather_id, description, "tomorrow"))
    lon = response.json()['city']['coord']['lon']
    lat = response.json()['city']['coord']['lat']
    send_location(chat_id, lon, lat)


def send_today_temperature(chat_id, place_en=None, lat=None, lon=None):
    if place_en is not None:
        response = get_response_for_city_by_city(place_en, urls.API_BASE_URL)
    else:
        response = get_response_for_city_by_coord(lat, lon, urls.API_BASE_URL)
    if response.status_code != 200:
        return send_message(chat_id, texts.no_answer)
    weather_id = response.json()['weather'][0]['id']
    degrees = round(response.json()['main']['temp'])
    feels_like = round(response.json()['main']['feels_like'])
    place_en = translator.translate(response.json()['name'], dest="en").text.title()
    country = get_country(response, 'sys')
    description = response.json()['weather'][0]['description']
    send_message(chat_id, form_answer(place_en, country, degrees, weather_id, description, "today", feels_like))
    lon = response.json()['coord']['lon']
    lat = response.json()['coord']['lat']
    send_location(chat_id, lon, lat)


def get_place(chat_id, place, when):
    place_en = translator.translate(place, dest="en").text.title()
    coord = get_response_for_coord_by_city(place_en)
    if len(coord.json()) > 1:
        keyboard = form_keyboard(coord)
        return send_dice(chat_id, json.dumps(keyboard))
    if when == "today":
        return send_today_temperature(chat_id, place_en=place_en)
    if when == "tomorrow":
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
    if users[chat_id] == "tomorrow":
        return send_tomorrow_temperature(chat_id, lat=lat, lon=lon)
    return send_message(chat_id, texts.forgot)


def parse_text(chat_id, text):
    if users[chat_id]:
        get_place(chat_id, text, users[chat_id])
    else:
        send_message(chat_id, texts.forgot)


def parse_command(chat_id, command):
    text = None
    if " " in command:
        command, text = command.split(" ")
    if command == "/start":
        start_command(chat_id)
    elif command == "/help":
        help_command(chat_id)
    elif command == "/today" or command == "/tomorrow":
        users[chat_id] = command[1:]
        if text is not None:
            parse_callback_query(chat_id, text)
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
