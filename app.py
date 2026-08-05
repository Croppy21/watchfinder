from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from services.tmdb import (
    search_multi,
    get_movie,
    get_watch_providers,
    get_tv_show,
    get_tv_watch_providers,
)

from utils.search import rank_results, did_you_mean_top3
from utils.formatting import poster_url, build_providers_html


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# -------------------------
# HOME PAGE
# -------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "request": request
        }
    )


# -------------------------
# SEARCH PAGE
# -------------------------

@app.get("/search", response_class=HTMLResponse)
def search_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "request": request
        }
    )


# -------------------------
# SEARCH RESULTS (HTMX)
# -------------------------

@app.get("/api/search", response_class=HTMLResponse)
def search(request: Request, query: str):

    data = search_multi(query)
    results = data.get("results", [])

    if not results:

        suggestions = did_you_mean_top3(query)

        return templates.TemplateResponse(
            request=request,
            name="partials/results.html",
            context={
                "request": request,
                "results": [],
                "suggestions": suggestions,
                "query": query
            }
        )


    results = rank_results(query, results)

    return templates.TemplateResponse(
        request=request,
        name="partials/results.html",
        context={
            "request": request,
            "results": results[:10],
            "suggestions": [],
            "query": query
        }
    )


# -------------------------
# MOVIE PAGE
# -------------------------

@app.get("/movie/{movie_id}", response_class=HTMLResponse)
def movie(request: Request, movie_id: int):

    movie = get_movie(movie_id)
    providers = get_watch_providers(movie_id)

    return templates.TemplateResponse(
        request=request,
        name="movie.html",
        context={
            "request": request,
            "movie": movie,
            "poster": poster_url(movie.get("poster_path")),
            "backdrop": movie.get("backdrop_path"),
            "providers_html": build_providers_html(providers)
        }
    )


# -------------------------
# TV PAGE
# -------------------------

@app.get("/tv/{tv_id}", response_class=HTMLResponse)
def tv(request: Request, tv_id: int):

    tv = get_tv_show(tv_id)
    providers = get_tv_watch_providers(tv_id)

    return templates.TemplateResponse(
        request=request,
        name="tv.html",
        context={
            "request": request,
            "tv": tv,
            "poster": poster_url(tv.get("poster_path")),
            "backdrop": tv.get("backdrop_path"),
            "providers_html": build_providers_html(providers)
        }
    )


# -------------------------
# AUTOCOMPLETE (HTMX)
# -------------------------

@app.get("/autocomplete", response_class=HTMLResponse)
def autocomplete(request: Request, query: str):

    if len(query.strip()) < 2:
        return ""

    data = search_multi(query)

    results = rank_results(query, data.get("results", []))[:8]

    return templates.TemplateResponse(
        request=request,
        name="partials/autocomplete.html",
        context={
            "request": request,
            "results": results
        }
    )

@app.get("/watchlist", response_class=HTMLResponse)
def watchlist(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="watchlist.html",
        context={
            "request": request
        }
    )
    
@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "request": request
        }
    )