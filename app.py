from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from services.tmbd import search_movie, get_movie, get_watch_providers
from utils.formatting import poster_url, build_providers_html

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

            .movie-btn {
                display: flex;
                gap: 10px;
                align-items: center;
                width: 100%;
                padding: 10px;
                margin: 6px 0;
                cursor: pointer;
                text-align: left;
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