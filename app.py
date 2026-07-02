from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from services.tmdb import (
    search_multi,
    get_movie,
    get_watch_providers,
    get_tv_show,
    get_tv_watch_providers,
)

from utils.formatting import (
    poster_url,
    build_providers_html
)

app = FastAPI()

# -------------------------
# HOME
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
            body {
                font-family: Arial;
                max-width: 900px;
                margin: 40px auto;
            }

            .result-btn {
                display: flex;
                gap: 10px;
                align-items: center;
                width: 100%;
                padding: 10px;
                margin: 6px 0;
                cursor: pointer;
                text-align: left;
            }

            .tag {
                font-size: 12px;
                opacity: 0.7;
            }
        </style>
    </head>

    <body>
        <h1>🎬 WatchFinder</h1>

        <form hx-get="/search" hx-target="#results">
            <input name="query" placeholder="Search movies or TV shows..." required />
            <button type="submit">Search</button>
        </form>

        <div id="results"></div>
    </body>
    </html>
    """


# -------------------------
# SEARCH (MOVIES + TV)
# -------------------------

@app.get("/search", response_class=HTMLResponse)
def search(query: str):

    data = search_multi(query)
    results = data.get("results", [])

    if not results:
        return "<h3>No results found</h3>"

    html = "<h2>Results</h2>"

    for item in results[:10]:

        media_type = item.get("media_type")

        # Decide type
        if media_type == "tv":
            title = item.get("name", "Unknown Show")
            endpoint = "tv"
        else:
            title = item.get("title", "Unknown Movie")
            endpoint = "movie"

        year = (
            item.get("release_date")
            or item.get("first_air_date")
            or ""
        )[:4]

        poster = poster_url(item.get("poster_path"))

        html += f"""
        <button
            class="result-btn"
            hx-get="/{endpoint}/{item['id']}"
            hx-target="#results"
        >
            <img src="{poster}" width="60" />

            <div>
                <b>{title}</b><br/>
                <small class="tag">{media_type.upper()}</small><br/>
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

        <button hx-get="/" hx-target="body">
            ← Home
        </button>

        <div style="display:flex; gap:20px; margin-top:15px;">
            <img src="{poster}" width="150" />

            <div>
                <h2>{movie.get('title')}</h2>
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


# -------------------------
# TV SHOW PAGE
# -------------------------

@app.get("/tv/{tv_id}", response_class=HTMLResponse)
def tv_show(tv_id: int):

    tv = get_tv_show(tv_id)
    providers = get_tv_watch_providers(tv_id)
    poster = poster_url(tv.get("poster_path"))
    providers_html = build_providers_html(providers)

    return f"""
    <div>

        <button hx-get="/" hx-target="body">
            ← Home
        </button>

        <div style="display:flex; gap:20px; margin-top:15px;">
            <img src="{poster}" width="150" />

            <div>
                <h2>{tv.get('name')}</h2>
                <p><b>First Air Date:</b> {tv.get('first_air_date','')[:4]}</p>
                <p><b>Rating:</b> {tv.get('vote_average')}</p>
                <p>{tv.get('overview')}</p>
            </div>
        </div>

        <hr/>

        <h2>Where to watch (AU)</h2>
        {providers_html}

    </div>
    """