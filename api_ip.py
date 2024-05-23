from flask import Flask, jsonify, request
import csv
import os
import os.path
import re
import random
import json
import requests
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import ipinfo
import urllib

load_dotenv()

dirname = os.path.dirname(__file__)


# ipinfo

url = 'http://ipinfo.io/json'
access_token = '854b39ba27faef'
handler = ipinfo.getHandlerAsync(access_token)

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
def load_places():
    with open(os.path.join(dirname,'./data/places.csv'), newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            places.append("".join(row))

def load_weather():
    with open(os.path.join(dirname,'./data/weather.csv'), newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            weather.append("".join(row))

def load_sounds():
    with open(os.path.join(dirname,'./data/sounds.csv'), newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            sounds.append("".join(row))

def load_snacks():
    with open(os.path.join(dirname,'./data/snacks.csv'), newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            snacks.append("".join(row))

def load_books():
    with open(os.path.join(dirname,'./data/books.csv'), newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            books.append("".join(row))

def load_textures():
    with open(os.path.join(dirname,'./data/textures.csv'), newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            textures.append("".join(row))

def load_creatures():
    with open(os.path.join(dirname,'./data/creatures.csv'), newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            creatures.append("".join(row))

def load_instruments():
    with open(os.path.join(dirname,'./data/instruments.csv'), newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            instruments.append("".join(row))

load_places()
load_weather()
load_sounds()
load_snacks()
load_books()
load_creatures()
load_textures()
load_instruments()

# def refresh_package():
#     package = {"place": places[random.randint(0, len(places)-1)], "weather": weather[random.randint(0, len(weather)-1)], "sounds": sounds[random.randint(0, len(sounds)-1)], "snacks": snacks[random.randint(0, len(snacks)-1)], "books": books[random.randint(0, len(books)-1)] }
#     return package

print("hello early?")


# def get_ip(response, request_ip):
#     url = 'http://ipinfo.io/' + request_instance[request_ip] + "/json"
#     # url = 'http://ipinfo.io/' + "86.11.205.0" + "/json"
#     response = urllib.request.urlopen(url)
#     ip_data = json.load(response)
#     # request_instance["location"] = ip_data["city"]
#     print(ip_data)

loop = asyncio.get_event_loop()

tempip = "5.74.185.15"

async def do_req(ip_addr):
    url = 'http://ipinfo.io/' + ip_addr + "/json" + "?token=854b39ba27faef"
    # url = 'http://ipinfo.io/' + tempip + "/json" + "?token=854b39ba27faef"
    # loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, requests.get, url)
    response = await future
    # details = await handler.getDetails(ip_address)
    # print(ip_address)
    # ip_data = json.load(details)
    # print(ip_data)
    ip_data = response.text
    ip_json = json.loads(ip_data)
    # print(ip_json)
    if "city" in ip_json:
        print("no city key")
        return ip_json["city"]
    else:
        return "Shiraz"



@app.route('/requests')

def ip():

    requests = []
    if os.path.isfile("ip.txt"):
        # print("ip.txt", "exists")
        with open("ip.txt", "r") as f:
            for lines in f:
                request_instance = {"date" : "", "time" : "", "ip_addr" : "", "ip_http_x" : "", "location" : ""}
                items = lines.split(" ")
                cleaned_item = []
                # items = [2024-05-21, 16:41:17.809057, 192.168.0.201, 192.168.0.201\n]
                # request_instance = {"date" : "", "time" : "", "ip_addr" : "", "ip_http_x" : "", "location" : ""}
                for item in items:
                    stripped_item = item.strip()
                    # print(stripped_item)
                    cleaned_item.append(stripped_item)
                    
                request_instance.update(dict(zip(request_instance, cleaned_item)))

                city = loop.run_until_complete(do_req(request_instance["ip_http_x"]))
                # print(city)
                
                request_instance["location"] = city

                requests.append(request_instance)
                # print(requests)

        # print(requests)
        # for request in requests:
        #     print(request["ip_http_x"])
        #     ip = request["ip_http_x"]

        #     loop.run_until_complete(do_req(ip))

        return requests

@app.route('/', methods=["GET"])


def home():

    # get ip and date

    date = str(datetime.now())
    ip_addr = request.environ['REMOTE_ADDR']
    ip_http_x = request.environ.get('HTTP_X_FORWARDED_FOR' , request.remote_addr)

    city = loop.run_until_complete(do_req(ip_http_x))
    print(city)

    if os.path.isfile("ip.txt"):
        with open("ip.txt", "a") as f:
            print("ip_addr.txt already exists")
            f.write(date + " " + ip_addr + " " + ip_http_x + " " + city + "\n")
            print("adding", ip_addr, ip_http_x)
    else:
        with open("ip.txt", "w") as f:
            f.write(date + " " + ip_addr + " " + ip_http_x + " " + city + "\n")
            print("writing", ip_addr, ip_http_x)


    # compose package

    package = { "fragments" : { "place": places[random.randint(0, len(places)-1)], "weather": weather[random.randint(0, len(weather)-1)], "sounds": sounds[random.randint(0, len(sounds)-1)], "snacks": snacks[random.randint(0, len(snacks)-1)], "books": books[random.randint(0, len(books)-1)], "textures": textures[random.randint(0, len(textures)-1)], "creatures": creatures[random.randint(0, len(creatures)-1)], "instruments": instruments[random.randint(0, len(instruments)-1)] } }
    prompt = "do not directly use the words you are given. you use this information and compose a dream-like haiku, in the style of Haruki Murakami." + str(package)

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

    prompt = "interpret this poem (<100 words), as an omen of a person's love life and personal life. these signs come very clear to you, you give direct, detailed, instructions " + str(poem)

    # print(prompt, "package", package)

    completion = client.chat.completions.create(
      model="gpt-4o",
      # model="gpt-3.5-turbo",
      # model="gpt-4",
      messages=[
        {"role": "system", "content": "you are an fortune teller, reading the someone's fate through this haiku. you use the imperative, telling your client what they should do. sometimes you ask them direct questions. sometimes your statements are romantic, they can also be mysterious and threatening, but avoid cliches."},
        {"role": "user", "content": prompt}
      ]
    )

    interpretation = completion.choices[0].message.content
    package['interpretation'] = str(interpretation.replace("\n", " "))

    return package

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)





