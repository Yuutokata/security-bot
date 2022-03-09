import requests
import json


async def load():
    with open("phishing/data.json", "r") as file:
        data = json.load(file)
    return data


async def update():
    try:
        with open("phishing/data.json", "w") as file:
            json.dump([], file)
    except:
        pass
    r = requests.get("https://api.yuuto.de/phishing/database", headers={'content-type': 'application/json'})
    data = r.json()

    with open("phishing/data.json", "w") as file:
        json.dump(data, file)
