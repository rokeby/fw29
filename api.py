from flask import Flask, jsonify, request
import csv
import os
import os.path
import re
import random
import json
import requests
# import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, timedelta
import pickle
# import ipinfo
# import urllib

load_dotenv()

dirname = os.path.dirname(__file__)


# ipinfo

# url = 'http://ipinfo.io/json'
# access_token = '854b39ba27faef'
# handler = ipinfo.getHandlerAsync(access_token)

# data

places = []
weather = []
sounds = []
snacks = []
books = []
creatures = []
textures = []
instruments = []

package = ""

app = Flask(__name__)

client = OpenAI()
api_key = os.getenv("OPENAI_API_KEY")

# load places from csv
def load_data():
    data_files = {
        'places': places,
        'weather': weather,
        'sounds': sounds,
        'snacks': snacks,
        'books': books,
        'creatures': creatures,
        'textures': textures,
        'instruments': instruments
    }
    for key, value in data_files.items():
        with open(os.path.join(dirname, f'./data/{key}.csv'), newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                value.append("".join(row))

load_data()

# Cache management functions
CACHE_FILE = 'cache.pkl'

def load_cache():
    if os.path.isfile(CACHE_FILE):
        with open(CACHE_FILE, 'rb') as f:
            return pickle.load(f)
    return None

def save_cache(data):
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(data, f)

def generate_message():
    package = {
        "fragments": {
            "place": places[random.randint(0, len(places)-1)],
            "weather": weather[random.randint(0, len(weather)-1)],
            "sounds": sounds[random.randint(0, len(sounds)-1)],
            "snacks": snacks[random.randint(0, len(snacks)-1)],
            "books": books[random.randint(0, len(books)-1)],
            "textures": textures[random.randint(0, len(textures)-1)],
            "creatures": creatures[random.randint(0, len(creatures)-1)],
            "instruments": instruments[random.randint(0, len(instruments)-1)]
        }
    }


    prompt = f"do not directly use the words you are given. you use this information and compose a dream-like haiku, in the style of Haruki Murakami. {package}"

    completion = client.chat.completions.create(
        model="gpt-4o",
        # model="gpt-3.5-turbo",
        # model="gpt-4",
        messages=[
            {"role": "system", "content": "you are an archaeologist of few words, but you have deep and unsettling dreams in which you see the weird fates and absurd futures of those around you. you never speak in the first person. you only refer to specific events in the future. your tone is direct, understated, everything is typed in lowercase"},
            {"role": "user", "content": prompt}
        ]
    )

    poem = completion.choices[0].message.content
    package['haiku'] = str(poem.replace("\n", " "))

    prompt = f"interpret this poem (<100 words), as an omen of a person's love life and personal life. these signs come very clear to you, you give direct, detailed, instructions {poem}"

    completion = client.chat.completions.create(
        model="gpt-4o",
        # model="gpt-3.5-turbo",
        # model="gpt-4",
        messages=[
            {"role": "system", "content": "you are a fortune teller, reading someone's fate through this haiku. you use the imperative, telling your client what they should do. sometimes you ask them direct questions. sometimes your statements are romantic, they can also be mysterious and threatening, but avoid cliches."},
            {"role": "user", "content": prompt}
        ]
    )

    interpretation = completion.choices[0].message.content
    package['interpretation'] = str(interpretation.replace("\n", " "))

    # Save the generated message with a timestamp
    cache_data = {
        'timestamp': datetime.now(),
        'message': package
    }
    save_cache(cache_data)
    return package

@app.route('/', methods=["GET"])
def home():
    # Load the cache and check the timestamp
    cache_data = load_cache()
    if cache_data:
        cache_timestamp = cache_data['timestamp']
        if datetime.now() - cache_timestamp < timedelta(days=1):
            # Serve the cached message
            return cache_data['message']
    
    # Generate a new message if cache is outdated or missing
    package = generate_message()
    return package

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, use_reloader=False)





