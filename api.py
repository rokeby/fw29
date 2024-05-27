from flask import Flask, jsonify, request
import csv
import os
import os.path
import re
import random
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime, timedelta
import pickle
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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

# Email configurations
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
# RECIPIENT_EMAILS = ["weil.flora@gmail.com"]  # Change this to the recipient's email address
RECIPIENT_EMAILS = ["zhexi@mit.edu"]  # Change this to the recipient's email address
BCC_EMAIL = ["gary.zhexi.zhang@gmail.com"]

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

def send_email(package):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ", ".join(RECIPIENT_EMAILS)
    msg['Subject'] = f""" {package['haiku']} """

    body = f"""
    <p><i>{package['fragments']['place']}, {package['fragments']['weather']}, {package['fragments']['sounds']}, {package['fragments']['snacks']}, {package['fragments']['books']}, {package['fragments']['textures']}, {package['fragments']['creatures']}</i></p>
    <p><i>{package['interpretation']}</i></p>
    <p>{datetime.now()}</p>

    """

    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAILS + BCC_EMAIL, msg.as_string())

def generate_message():

    print("start generate_message()")

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

    print("bulding haiku")

    prompt = f"do not directly use the words you are given. you use this information and compose a dream-like haiku, in the style of Haruki Murakami, with a line break between each line. {package}"

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

    print("completed haiku")
    print("bulding interpretation")

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

    print("completed interpretation")

    # Save the generated message with a timestamp
    cache_data = {
        'timestamp': datetime.now(),
        'message': package
    }
    save_cache(cache_data)

    print("saved package as cache_data")

    # Send the package via email
    print(datetime.now(), "sending package as email to", RECIPIENT_EMAILS, BCC_EMAIL)
    send_email(package)

    return package

def get_oracle():
    cache_data = load_cache()
    if cache_data:
        cache_timestamp = cache_data['timestamp']
        if datetime.now() - cache_timestamp < timedelta(days=1):
            # Serve the cached message
            print(datetime.now(), "\n cached message less than 1 day old, returning cached message \n", cache_data["message"], "\n generated at:", cache_timestamp)
            return cache_data['message']
    
    # Generate a new message if cache is outdated or missing
    print(datetime.now(), "cached message outdated or missing, generating new message")
    package = generate_message()
    print(datetime.now(), "\n", "cached message:", package)
    return package

get_oracle()

@app.route('/')
def home():
    package = load_cache()
    return package

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, use_reloader=False)





