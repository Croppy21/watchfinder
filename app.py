from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from config import TMDB_READ_ACCESS_TOKEN

app = FastAPI()

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w200"


# -------------------------
# TMDB API (BEARER ONLY)
# -------------------------

def tmdb_get(url: str, params: dict | None = None):
    headers = {
        "Authorization": f"Bearer {TMDB_READ_ACCESS_TOKEN}",
        "accept": "application/json"
    }

    return requests.get(url, headers=headers, params=params or {}).json()


def search_movie(query: str):
    url = f"{BASE_URL}/search/movie"
    return tmdb_get(url, {"query": query})


def get_movie(movie_id: int):
    url = f"{BASE_URL}/movie/{movie_id}"
    return tmdb_get(url)


def get_watch_providers(movie_id: int):
    url = f"{BASE_URL}/movie/{movie_id}/watch/providers"
    return tmdb_get(url)


# -------------------------
# HELPERS
# -------------------------

def poster_url(path):
    if not path:
        return "https://via.placeholder.com/100x150?text=No+Image"
    return f"{IMAGE_BASE}{path}"


def normalize_provider_name(name: str) -> str:
    name = name.strip()

    replacements = {
        "Amazon Prime Video with Ads": "Amazon Prime Video",
        "Amazon Prime Video (Channel)": "Amazon Prime Video",
        "Netflix with Ads": "Netflix",
        "Netflix Standard with Ads": "Netflix",
        "Netflix Basic with Ads": "Netflix",
        "HBO Max Amazon Channel": "HBO Max",
        "Max": "HBO Max",
        "Apple TV Store": "Apple TV",
        "Google Play Movies": "Google Play",
    }

    # exact match
    if name in replacements:
        return replacements[name]

    # generic cleanup
    if " with Ads" in name:
        return name.replace(" with Ads", "").strip()

    return name


def build_providers_html(providers_data):
    au = providers_data.get("results", {}).get("AU")

    if not au:
        return "<p><i>No streaming data available in Australia.</i></p>"

    html = ""

    for key, label in {
        "flatrate": "Streaming",
        "rent": "Rent",
        "buy": "Buy"
    }.items():

        if key not in au:
            continue

        seen = set()
        section = ""

        for p in au[key]:
            name = normalize_provider_name(p["provider_name"])

            if name in seen:
                continue

            seen.add(name)
            section += f"<li>{name}</li>"

        if section:
            html += f"<h3>{label}</h3><ul>{section}</ul>"

    return html or "<p>No providers found.</p>"


# -------------------------
# HOME PAGE
# -------------------------

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WatchFinder</title>
        <script src="https://unpkg.com/htmx.org@1.9.12"></script>

        <style>
            body { font-family: Arial; max-width: 900px; margin: 40px auto; }
            .movie-btn {
                display:flex;
                gap:10px;
                align-items:center;
                width:100%;
                padding:10px;
                margin:6px 0;
                cursor:pointer;
            }
        </style>
    </head>

    <body>
        <h1>🎬 WatchFinder</h1>

        <form hx-get="/search" hx-target="#results">
            <input name="query" placeholder="Search movies..." required />
            <button type="submit">Search</button>
        </form>

        <div id="results"></div>
    </body>
    </html>
    """


# -------------------------
# SEARCH
# -------------------------

@app.get("/search", response_class=HTMLResponse)
def search(query: str):

    data = search_movie(query)
    results = data.get("results", [])

    if not results:
        return "<h3>No movies found</h3>"

    html = "<h2>Results</h2>"

    for movie in results[:10]:
        year = movie.get("release_date", "")[:4]
        poster = poster_url(movie.get("poster_path"))

        html += f"""
        <button
            class="movie-btn"
            hx-get="/movie/{movie['id']}"
            hx-target="#results"
        >
            <img src="{poster}" width="60" />
            <div>
                <b>{movie['title']}</b><br/>
                <small>{year}</small>
            </div>
        </button>
        """

    return html


# -------------------------
# MOVIE PAGE
# -------------------------

@app.get("/movie/{movie_id}", response_class=HTMLResponse)
def movie(movie_id: int):

    movie = get_movie(movie_id)
    providers = get_watch_providers(movie_id)

    poster = poster_url(movie.get("poster_path"))
    providers_html = build_providers_html(providers)

    return f"""
    <div>

        <button hx-get="/search?query={movie['title']}" hx-target="#results">
            ← Back
        </button>

        <div style="display:flex; gap:20px; margin-top:15px;">
            <img src="{poster}" width="150" />

            <div>
                <h2>{movie['title']}</h2>
                <p><b>Year:</b> {movie.get('release_date','')[:4]}</p>
                <p><b>Rating:</b> {movie.get('vote_average')}</p>
                <p>{movie.get('overview')}</p>
            </div>
        </div>

        <hr/>

        <h2>Where to watch (AU)</h2>
        {providers_html}

    </div>
    """