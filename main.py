from dotenv import load_dotenv
import os
from os.path import join, dirname
from googletrans import Translator
import country_converter as coco
from flask import Flask, request
import json
import requests
import urls
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
    if parse_mode is None:
        data = {"chat_id": chat_id, "text": text}
    else:
        data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "reply_markup": reply_markup}
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


def get_response_for_city(city, url):
    param_request = {'q': city, 'appid': get_from_env("API_KEY"), 'cnt': 1, 'units': 'metric'}
    response = requests.get(url, params=param_request)
    return response


def get_country(r, t='sys'):
    try:
        country = r.json()[t]['country']
        if country != '':
            return coco.convert(names=country, to='name_short')
    except KeyError:
        return None
    return None


def send_tomorrow_temperature(chat_id, place):
    place_en = translator.translate(place, dest="en").text.title()
    print(place_en)
    response = get_response_for_city(place_en, urls.API_FORECAST_URL)
    if response.status_code != 200:
        return send_message(chat_id, 'Я не знаю ответа на ваш запрос, извините.')
    degrees = round(response.json()['list'][0]['main']['temp'])
    country = get_country(response, 'city')
    answer = 'In ' + place_en
    if country is not None and country != place_en:
        answer += ' (' + country + ')'
    answer += ' will be ' + str(degrees) + ' degrees tomorrow.'
    answer = translator.translate(answer, dest="ru").text
    return send_message(chat_id, answer)


def send_temperature(chat_id, place):
    place_en = translator.translate(place, "en").text.title()
    print(place_en)
    response = get_response_for_city(place_en, urls.API_BASE_URL)
    if response.status_code != 200:
        return send_message(chat_id, 'Я не знаю ответа на ваш запрос, извините.')
    degrees = round(response.json()['main']['temp'])
    feels_like = round(response.json()['main']['feels_like'])
    country = get_country(response)
    answer = 'In ' + place_en
    if country is not None and country != place_en:
        answer += ' (' + country + ')'
    answer += ' is ' + str(degrees) + ' degrees right now. Feels like ' + str(feels_like) + ' degrees.'
    answer = re.sub('это ', '', translator.translate(answer, "ru").text)
    return send_message(chat_id, answer)
    # lon = response.json()['coord']['lon']
    # lat = response.json()['coord']['lat']
    # send_location(chat_id, lon, lat)


def start_command(chat_id):
    info = "Привет, я готов предоставить тебе прогноз погоды по всему миру.\n\n" + \
           "Напиши /help, если хочешь узнать, что я умею, или если тебе нужна помощь."
    send_message(chat_id, info)


def help_command(chat_id):
    info = "Сейчас я расскажу, что я умею:\n\n" + \
           "/today — включение режима *\"здесь и сейчас!\"*\n" + \
           "/tomorrow — включение режима *\"а что же будет завтра?\"*\n\n" + \
           "После выбора режима напиши город, страну или континент, а затем я постараюсь тебе подсказать, " + \
           "какая температура в этом месте сейчас или какая температура там будет завтра.\n" + \
           "Заметь, режим каждый раз выбирать не нужно, ведь я умный бот и помню что ты выбрал :)\n\n" + \
           "Если что-то не так или у вас возникли вопросы, вы всегда можете написать создателю этого бота."
    reply_markup = json.dumps({'inline_keyboard': [[{
        "text": "Написать разработчику",
        "url": "telegram.me/penguiners"
    }]]})
    send_message(chat_id, info, 'Markdown', reply_markup)


def is_command(r):
    try:
        if r.json["message"]["entities"][0]["type"] == "bot_command":
            return True
    except KeyError:
        return False
    return False


def parse_text(chat_id, text):
    if users[chat_id] == "today":
        send_temperature(chat_id, text)
    elif users[chat_id] == "tomorrow":
        send_tomorrow_temperature(chat_id, text)
    else:
        send_message(chat_id, "Вы забыли включить режим. Используй команду /help, чтобы узнать подробнее" +
                     " как его включить.")


def parse_command(chat_id, text):
    if text == "/start":
        start_command(chat_id)
    elif text == "/help":
        help_command(chat_id)
    elif text == "/today" or text == "/tomorrow":
        users[chat_id] = text[1:]
    else:
        send_message(chat_id, "Я не знаю такой команды :(")


@app.route("/", methods=["POST"])
def processing():
    logging(request.json)
    chat_id = request.json["message"]["chat"]["id"]

    try:
        users[chat_id]
    except KeyError:
        users[chat_id] = ""

    try:
        text = request.json["message"]["text"]
    except KeyError:
        send_message(chat_id, "Я вас не понимаю :(")
        return {"ok": True}

    if is_command(request):
        parse_command(chat_id, text)
    else:
        parse_text(chat_id, text)

    print(users)
    return {"ok": True}


if __name__ == "__main__":
    app.run()
