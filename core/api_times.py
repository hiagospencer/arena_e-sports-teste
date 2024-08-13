import requests
from .models import *

def get_api_data():
    emblemas_times_ingles()
    emblemas_times_italiano()
    emblemas_times_frances()
    emblemas_times_espanhol()
    emblemas_times_alemao()
    emblemas_times_brasileiro()


def get_api_eafc():
    url = "https://drop-api.ea.com/rating/fc-24"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data

def emblemas_times_ingles():
    url = "https://www.thesportsdb.com/api/v1/json/3/lookuptable.php?l=4328&s=2023-2024"
    response = requests.get(url)
    times = []
    emblemas = []
    if response.status_code == 200:
        data = response.json()
        for item in data['table']:
            print(item['strTeam'])
            times = TimesEmblemas.objects.create(
                time=item['strTeam'],
                emblema=item['strBadge']
            )
            times.save()

    else:
        print("Não foi possivel conectar a API")

def emblemas_times_italiano():
    url = "https://www.thesportsdb.com/api/v1/json/3/lookuptable.php?l=4332&s=2023-2024"
    response = requests.get(url)
    times = []
    emblemas = []
    if response.status_code == 200:
        data = response.json()
        for item in data['table']:
            print(item['strTeam'])
            times = TimesEmblemas.objects.create(
                time=item['strTeam'],
                emblema=item['strBadge']
            )

    else:
        print("Não foi possivel conectar a API")


def emblemas_times_alemao():
    url = "https://www.thesportsdb.com/api/v1/json/3/lookuptable.php?l=4331&s=2022-2023"
    response = requests.get(url)
    times = []
    emblemas = []
    if response.status_code == 200:
        data = response.json()
        for item in data['table']:
            print(item['strTeam'])
            times = TimesEmblemas.objects.create(
                time=item['strTeam'],
                emblema=item['strBadge']
            )

    else:
        print("Não foi possivel conectar a API")


def emblemas_times_frances():
    url = "https://www.thesportsdb.com/api/v1/json/3/lookuptable.php?l=4334&s=2022-2023"
    response = requests.get(url)
    times = []
    emblemas = []
    if response.status_code == 200:
        data = response.json()
        for item in data['table']:
            print(item['strTeam'])
            times = TimesEmblemas.objects.create(
                time=item['strTeam'],
                emblema=item['strBadge']
            )

    else:
        print("Não foi possivel conectar a API")

def emblemas_times_espanhol():
    url = "https://www.thesportsdb.com/api/v1/json/3/lookuptable.php?l=4335&s=2022-2023"
    response = requests.get(url)
    times = []
    emblemas = []
    if response.status_code == 200:
        data = response.json()
        for item in data['table']:
            print(item['strTeam'])
            times = TimesEmblemas.objects.create(
                time=item['strTeam'],
                emblema=item['strBadge']
            )

    else:
        print("Não foi possivel conectar a API")

def emblemas_times_brasileiro():
    url = "https://www.thesportsdb.com/api/v1/json/3/lookuptable.php?l=4351&s=2024"
    response = requests.get(url)
    times = []
    emblemas = []
    if response.status_code == 200:
        data = response.json()
        for item in data['table']:
            print(item['strTeam'])
            times = TimesEmblemas.objects.create(
                time=item['strTeam'],
                emblema=item['strBadge']
            )

    else:
        print("Não foi possivel conectar a API")
