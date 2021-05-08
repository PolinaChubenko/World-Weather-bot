import os
from os.path import join, dirname
import json
import requests
from dotenv import load_dotenv
import urls


def get_from_env(key):
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key)


def send_message(chat_id, text, parse_mode=None, reply_markup=None):
    method = "sendMessage"
    token = get_from_env("BOT_TOKEN")
    url = urls.TELEGRAM_BOT_URL + f"{token}/{method}"
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode,
            "reply_markup": reply_markup}
    requests.post(url, data=data)


def send_dice(chat_id, reply_markup):
    method = "sendDice"
    token = get_from_env("BOT_TOKEN")
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


def get_response_for_coord_by_city(city):
    url = urls.API_GEOCODING_URL
    param_request = {'q': city, 'limit': urls.LIMIT, 'appid': get_from_env("API_KEY")}
    response = requests.get(url, params=param_request)
    return response


def get_response_for_city_by_city(city, url):
    param_request = {'q': city, 'appid': get_from_env("API_KEY"),
                     'lang': 'ru', 'cnt': 1, 'units': 'metric'}
    response = requests.get(url, params=param_request)
    return response


def get_response_for_city_by_coord(lat, lon, url):
    param_request = {'lat': lat, 'lon': lon, 'appid': get_from_env("API_KEY"), 'lang': 'ru',
                     'cnt': 1, 'units': 'metric'}
    response = requests.get(url, params=param_request)
    return response
