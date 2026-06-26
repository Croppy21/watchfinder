from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from config import TMDB_READ_ACCESS_TOKEN

app = FastAPI()

BASE_URL = "https://api.themoviedb.org/3"


# -------------------------
# TMDB
# -------------------------

def search_movie(query: str):
    url = f"{BASE_URL}/search/movie"

    headers = {
        "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}",
        "accept": "application/json"
    }

    return requests.get(url, headers=headers, params={"query": query}).json()


def get_watch_providers(movie_id: int):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"

    headers = {
        "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}",
        "accept": "application/json"
    }

    return requests.get(url, headers=headers).json()


# -------------------------
# HTML UI
# -------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WatchFinder</title>
        <script src="https://unpkg.com/htmx.org@1.9.12"></script>
    </head>

    <body>
        <h1>🎬 WatchFinder</h1>

        <input
            type="text"
            name="query"
            placeholder="Search movies..."
            hx-get="/search"
            hx-trigger="keyup changed delay:400ms"
            hx-target="#results"
        />

        <div id="results"></div>
    </body>
    </html>
    """


# -------------------------
# HTMX SEARCH ENDPOINT (HTML RESPONSE)
# -------------------------

@app.get("/search", response_class=HTMLResponse)
def search(query: str):

    if not query:
        return "<p>Type to search...</p>"

    data = search_movie(query)
    results = data.get("results", [])

    if not results:
        return "<p>No results found</p>"

    movie = results[0]

    providers_data = get_watch_providers(movie["id"])
    au = providers_data.get("results", {}).get("AU", {})

    providers_html = ""

    for key, label in {
        "flatrate": "Subscription",
        "rent": "Rent",
        "buy": "Buy"
    }.items():

        if key in au:
            providers_html += f"<h4>{label}</h4><ul>"
            for p in au[key]:
                providers_html += f"<li>{p['provider_name']}</li>"
            providers_html += "</ul>"

    return f"""
    <div style="border:1px solid #ccc; padding:10px; margin-top:10px;">
        <h2>{movie.get('title')}</h2>
        <p><b>Year:</b> {movie.get('release_date','')[:4]}</p>
        <p><b>Rating:</b> {movie.get('vote_average')}</p>
        <p>{movie.get('overview')}</p>

        {providers_html}
    </div>
    """