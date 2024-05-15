import requests

def search_location(query):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data.get('results', [])