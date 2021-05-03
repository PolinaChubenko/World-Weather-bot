from dotenv import load_dotenv
import os
from os.path import join, dirname
from googletrans import Translator
from flask import Flask, request
import json
import requests
import urls


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


def logging(data, filename="log.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_response_for_city(city, url):
    param_request = {'q': city, 'appid': get_from_env("API_KEY"), 'units': 'metric'}
    response = requests.get(url, params=param_request)
    return response


def get_temperature(chat_id, city):
    city_en = translator.translate(city, dest="en").text.lower()
    response = get_response_for_city(city_en, urls.API_BASE_URL)
    if response.status_code != 200:
        send_message(chat_id, 'Похоже такого города нет, извините.')
    else:
        degrees = round(response.json()['main']['temp'])
        answer = 'It\'s ' + str(degrees) + ' degrees in ' + city_en.title() + '.'
        answer = translator.translate(answer, dest="ru").text
        send_message(chat_id, answer)


def is_command(r):
    try:
        if r.json["message"]["entities"][0]["type"] == "bot_command":
            return True
    except KeyError:
        return False
    return False


@app.route("/", methods=["POST"])
def processing():
    logging(request.json)
    chat_id = request.json["message"]["chat"]["id"]
    text = request.json["message"]["text"]
    print(is_command(request))
    get_temperature(chat_id, text)
    return {"ok": True}


if __name__ == "__main__":
    app.run()
