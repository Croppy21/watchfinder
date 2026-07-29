import requests
from config import TMDB_READ_ACCESS_TOKEN

BASE_URL = "https://api.themoviedb.org/3"

HEADERS = {
    "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}",
    "accept": "application/json"
}

titles_cache = []


# -------------------------
# INTERNAL FETCH
# -------------------------
def _fetch(endpoint: str, page: int = 1):
    return requests.get(
        f"{BASE_URL}/{endpoint}",
        headers=HEADERS,
        params={"page": page}
    ).json()


# -------------------------
# CLEAN TITLE (IMPORTANT FIX)
# -------------------------
def _clean_title(title: str) -> str:
    if not title:
        return ""

    return (
        title
        .replace(":", "")
        .replace("-", " ")
        .replace("  ", " ")
        .strip()
    )


# -------------------------
# ADD ITEM SAFELY
# -------------------------
def _add_item(item, key: str, media_type: str):
    title = item.get(key)

    if not title:
        return

    clean = _clean_title(title)

    titles_cache.append({
        "title": title,
        "clean_title": clean,
        "id": item.get("id"),
        "type": media_type
    })


# -------------------------
# BUILD CACHE
# -------------------------
def build_cache(pages: int = 10):

    global titles_cache
    titles_cache = []

    # -------------------------
    # MOVIES
    # -------------------------
    for page in range(1, pages + 1):
        data = _fetch("movie/popular", page)
        for m in data.get("results", []):
            _add_item(m, "title", "movie")

    for page in range(1, pages + 1):
        data = _fetch("movie/top_rated", page)
        for m in data.get("results", []):
            _add_item(m, "title", "movie")

    # -------------------------
    # TV SHOWS
    # -------------------------
    for page in range(1, pages + 1):
        data = _fetch("tv/popular", page)
        for t in data.get("results", []):
            _add_item(t, "name", "tv")

    for page in range(1, pages + 1):
        data = _fetch("tv/top_rated", page)
        for t in data.get("results", []):
            _add_item(t, "name", "tv")

    # -------------------------
    # TRENDING
    # -------------------------
    for page in range(1, pages + 1):
        data = _fetch("trending/all/week", page)

        for item in data.get("results", []):
            if item.get("media_type") == "movie":
                _add_item(item, "title", "movie")
            elif item.get("media_type") == "tv":
                _add_item(item, "name", "tv")


# -------------------------
# GET CACHE
# -------------------------
def get_cache():
    return titles_cache


# -------------------------
# DEBUG
# -------------------------
def cache_size():
    return len(titles_cache)