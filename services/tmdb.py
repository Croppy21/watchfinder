import requests
from config import TMDB_READ_ACCESS_TOKEN

BASE_URL = "https://api.themoviedb.org/3"


def _get(url: str, params: dict | None = None):
    headers = {
        "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}",
        "accept": "application/json"
    }

    response = requests.get(url, headers=headers, params=params or {})

    # optional debug
    if response.status_code != 200:
        print("TMDB ERROR:", response.status_code, response.text)

    return response.json()


def search_movie(query: str):
    return _get(f"{BASE_URL}/search/movie", {"query": query})


def get_movie(movie_id: int):
    return _get(f"{BASE_URL}/movie/{movie_id}")


def get_watch_providers(movie_id: int):
    return _get(f"{BASE_URL}/movie/{movie_id}/watch/providers")

def search_multi(query: str):
    return _get(f"{BASE_URL}/search/multi", {"query": query})


def get_tv_show(tv_id: int):
    return _get(f"{BASE_URL}/tv/{tv_id}")


def get_tv_watch_providers(tv_id: int):
    return _get(f"{BASE_URL}/tv/{tv_id}/watch/providers")