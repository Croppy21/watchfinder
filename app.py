import os

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from utils.auth import hash_password, verify_password

from services.tmdb import (
    search_multi,
    get_movie,
    get_watch_providers,
    get_tv_show,
    get_tv_watch_providers,
)

from utils.search import (
    rank_results,
    rank_autocomplete_results,
    did_you_mean_top3
) 
from utils.formatting import poster_url, build_providers_html


app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY")
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# -------------------------
# AUTHENTICATION
# -------------------------

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        request.session.clear()
        return None

    return user


# -------------------------
# HOME PAGE
# -------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    success = request.session.pop("success", None)
    error = request.session.pop("error", None)

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "request": request,
            "success": success,
            "error": error
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
        context={"request": request}
    )


# -------------------------
# SEARCH RESULTS (HTMX)
# -------------------------
@app.get("/api/search", response_class=HTMLResponse)
def search(request: Request, query: str):

    data = search_multi(query)

    results = [
        item for item in data.get("results", [])
        if item.get("media_type") in ("movie", "tv")
    ]

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

    results = [
        item for item in data.get("results", [])
        if item.get("media_type") in ("movie", "tv")
    ]

    results = rank_autocomplete_results(query, results)[:8]

    return templates.TemplateResponse(
        request=request,
        name="partials/autocomplete.html",
        context={
            "request": request,
            "results": results
        }
    )

#-------------------------
# WATCHLIST PAGE
#------------------------
@app.get("/watchlist", response_class=HTMLResponse)
def watchlist(
    request: Request,
    user: User = Depends(get_current_user)
):

    if not user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="watchlist.html",
        context={
            "request": request,
            "user": user
        }
    )
    
# -------------------------
# PROFILE PAGE
# -------------------------
@app.get("/profile", response_class=HTMLResponse)
def profile(
    request: Request,
    user: User = Depends(get_current_user)
):

    if not user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "request": request,
            "user": user
        }
    )
    
    
# -------------------------
# LOGIN PAGE
# -------------------------
@app.get("/login", response_class=HTMLResponse)
def login(request: Request):

    success = request.session.pop("success", None)
    error = request.session.pop("error", None)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "success": success,
            "error": error
        }
    )
@app.post("/login", response_class=HTMLResponse)
def login_user(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    login = login.strip()

    user = (
        db.query(User)
        .filter(
            (User.username == login) |
            (User.email == login.lower())
        )
        .first()
    )

    if not user or not verify_password(password, user.password_hash):

        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "error": "Invalid username/email or password."
            }
        )

    request.session["user_id"] = user.id

    return RedirectResponse(
        url="/profile",
        status_code=303
    )

# -------------------------
# LOGOUT
# -------------------------
@app.get("/logout")
def logout(request: Request):

    request.session.clear()

    request.session["success"] = "You've been logged out."

    return RedirectResponse(
        url="/",
        status_code=303
    )

#-------------------------
# REGISTER PAGE
#------------------------
@app.get("/register", response_class=HTMLResponse)
def register(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "request": request
        }
    )

@app.post("/register", response_class=HTMLResponse)
def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    username = username.strip()
    email = email.strip().lower()

    existing_user = (
        db.query(User)
        .filter(
            (User.email == email) |
            (User.username == username)
        )
        .first()
    )

    if existing_user:

        if existing_user.email == email:
            error = "An account with that email already exists."
        else:
            error = "That username is already taken."

        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "request": request,
                "error": error,
                "username": username,
                "email": email
            }
        )

    hashed_password = hash_password(password)

    user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )

    db.add(user)
    db.commit()

    request.session["success"] = "Account created successfully. You can now log in."

    return RedirectResponse(
        url="/login",
        status_code=303
    )
    
# -------------------------
# SETTINGS PAGE
# -------------------------

@app.get("/settings", response_class=HTMLResponse)
def settings(
    request: Request,
    user: User = Depends(get_current_user)
):

    if not user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "request": request,
            "user": user
        }
    )