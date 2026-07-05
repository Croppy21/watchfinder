from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from services.title_cache import build_cache, cache_size
from services.tmdb import (
    search_multi,
    get_movie,
    get_watch_providers,
    get_tv_show,
    get_tv_watch_providers,
)

from utils.search import (
    rank_results,
    did_you_mean_top3
)

from utils.formatting import (
    poster_url,
    build_providers_html
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


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
        <link rel="stylesheet" href="/static/style.css">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>

    <body>
        <div class="container">

            <h1>🎬 WatchFinder</h1>

            <p class="subtitle">
            Find where to stream movies and TV shows
            </p>

            <form class="search-form"
                hx-get="/search"
                hx-target="#results">
                <input name="query" placeholder="Search movies or TV shows..." required />
                <button type="submit">Search</button>
            </form>
        </div>
        <div id="results"></div>
    </body>
    </html>
    """


# -------------------------
# STARTUP CACHE BUILD
# -------------------------
@app.on_event("startup")
def startup():
    build_cache(pages=5)
    print("CACHE SIZE:", cache_size())


# -------------------------
# SEARCH ROUTE
# -------------------------
@app.get("/search", response_class=HTMLResponse)
def search(query: str):

    # -------------------------
    # 1. NORMAL SEARCH
    # -------------------------
    data = search_multi(query)
    results = data.get("results", [])

    print("RAW COUNT:", len(results))

    # -------------------------
    # 2. NORMAL RESULTS FLOW
    # -------------------------
    if results:
        results = rank_results(query, results)

        html = "<h2>Results</h2>"

        for item in results[:10]:

            media_type = item.get("media_type")

            if media_type == "tv":
                title = item.get("name")
                endpoint = "tv"
            else:
                title = item.get("title")
                endpoint = "movie"

            year = (
                item.get("release_date")
                or item.get("first_air_date")
                or ""
            )[:4]

            poster = poster_url(item.get("poster_path"))

            html += f"""
            <button class="result-btn"
                    hx-get="/{endpoint}/{item['id']}"
                    hx-target="#results">

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
    # 3. DID YOU MEAN (FIXED)
    # -------------------------
    suggestions = did_you_mean_top3(query)

    if suggestions:
        html = "<h3>No exact results. Did you mean:</h3>"

        for s in suggestions:
            html += f"""
            <button class="result-btn"
                    hx-get="/search?query={s}"
                    hx-target="#results">
                {s}
            </button>
            """

        return html

    return "<h3>No results found</h3>"


# -------------------------
# MOVIE PAGE
# -------------------------
@app.get("/movie/{movie_id}", response_class=HTMLResponse)
def movie(movie_id: int):

    movie = get_movie(movie_id)
    providers = get_watch_providers(movie_id)

    poster = poster_url(movie.get("poster_path"))
    providers_html = build_providers_html(providers)

    backdrop_url = (
        f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}"
        if movie.get("backdrop_path")
        else ""
    )

    return f"""
    <div class="container">

        <button id="back-btn" hx-get="/" hx-target="body">Back</button>

        <div class="hero" style="background-image: url('{backdrop_url}');"></div>

        <div class="details">
            <img src="{poster}" />

            <div>
                <h2>{movie.get('title')}</h2>

                <div class="rating">
                    {movie.get('vote_average')}
                </div>

                <p>{movie.get('overview')}</p>
            </div>
        </div>

        <h3>Where to watch (AU)</h3>
        {providers_html}

    </div>
    """


# -------------------------
# TV PAGE
# -------------------------
@app.get("/tv/{tv_id}", response_class=HTMLResponse)
def tv(tv_id: int):

    tv = get_tv_show(tv_id)
    providers = get_tv_watch_providers(tv_id)

    poster = poster_url(tv.get("poster_path"))
    providers_html = build_providers_html(providers)

    backdrop_url = (
        f"https://image.tmdb.org/t/p/original{tv.get('backdrop_path')}"
        if tv.get("backdrop_path")
        else ""
    )
    return f"""
    <div class="container">

        <button  id="back-btn" hx-get="/" hx-target="body">Back</button>
        <div class="hero" style="background-image: url('{backdrop_url}');"></div>

        <div class="details">
            <img src="{poster}" width="150" />

            <div>
                <h2>{tv.get('name')}</h2>
                <p><b>First Air Date:</b> {tv.get('first_air_date','')[:4]}</p>
                <p class="rating">Rating: {tv.get('vote_average')}</p>
                <p>{tv.get('overview')}</p>
            </div>
        </div>

        <hr/>
        <h2>Where to watch (AU)</h2>
        {providers_html}
    </div>
    """
    
@app.get("/autocomplete", response_class=HTMLResponse)
def autocomplete(query: str):

    if len(query) < 2:
        return ""

    data = search_multi(query)

    results = rank_results(query, data.get("results", []))[:8]

    html = '<div class="autocomplete-box">'

    current = None

    for item in results:

        media = item["media_type"]

        if media != current:
            current = media
            html += f'<div class="autocomplete-header">{media.upper()}</div>'

        title = item.get("title") or item.get("name")

        year = (
            item.get("release_date")
            or item.get("first_air_date")
            or ""
        )[:4]

        endpoint = "movie" if media == "movie" else "tv"

        poster = poster_url(item.get("poster_path"))

        html += f"""
        <button
            class="autocomplete-item"
            hx-get="/{endpoint}/{item['id']}"
            hx-target="body">

            <img src="{poster}">

            <div>

                <strong>{title}</strong>

                <small>{year}</small>

            </div>

        </button>
        """

    html += "</div>"

    return html