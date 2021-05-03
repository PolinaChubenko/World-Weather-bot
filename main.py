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


def get_from_env(key):
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key)


def send_message(chat_id, text):
    method = "sendMessage"
    token = get_from_env("BOT_TOKEN")
    url = urls.TELEGRAM_BOT_URL + f"{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
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
    param_request = {'q': city, 'appid': get_from_env("API_KEY"), 'units': 'metric'}
    response = requests.get(url, params=param_request)
    print(response.text)
    return response


def get_country(r):
    try:
        country = r.json()['sys']['country']
        return coco.convert(names=country, to='name_short')
    except KeyError:
        return None


def send_temperature(chat_id, place):
    place_en = translator.translate(place, dest="en").text.title()
    response = get_response_for_city(place_en, urls.API_BASE_URL)
    if response.status_code != 200:
        send_message(chat_id, 'Я не знаю ответа на ваш запрос, извините.')
    else:
        degrees = round(response.json()['main']['temp'])
        feels_like = round(response.json()['main']['feels_like'])
        country = get_country(response)
        answer = 'In ' + place_en
        if country is not None and country != place_en:
            answer += ' (' + country + ')'
        answer += ' is ' + str(degrees) + ' degrees. Feels like ' + str(feels_like) + '.'
        answer = re.sub('это ', '', translator.translate(answer, dest="ru").text)
        send_message(chat_id, answer)
        # lon = response.json()['coord']['lon']
        # lat = response.json()['coord']['lat']
        # send_location(chat_id, lon, lat)


def start_command(chat_id):
    info = "Привет, я готов предоставить тебе прогноз погоды по всему миру.\n\n" + \
           "Напиши /help, если хочешь узнать, что я умею, или если тебе нужна помощь."
    send_message(chat_id, info)


def help_command(chat_id):
    info = "Сейчас я расскажу, чем я могу помочь тебе:\n\n" + \
           "Напиши город, страну или континент и я постараюсь тебе подсказать, какая температура сейчас " \
           "в этом месте."
    send_message(chat_id, info)


def is_command(r):
    try:
        if r.json["message"]["entities"][0]["type"] == "bot_command":
            return True
    except KeyError:
        return False
    return False


def parse_command(chat_id, text):
    if text == "/start":
        start_command(chat_id)
    elif text == "/help":
        help_command(chat_id)
    else:
        send_message(chat_id, "Я не знаю такой команды :(")


@app.route("/", methods=["POST"])
def processing():
    logging(request.json)
    chat_id = request.json["message"]["chat"]["id"]
    text = request.json["message"]["text"]
    if is_command(request):
        parse_command(chat_id, text)
    else:
        send_temperature(chat_id, text)
    return {"ok": True}


if __name__ == "__main__":
    app.run()
