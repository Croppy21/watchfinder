from datetime import datetime, timedelta, timezone
import os

import re, random

from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User, WatchlistItem
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
# Flash Messages (notifications)
# -------------------------

def set_flash(request: Request, message: str, category: str = "success"):
    request.session["flash"] = {
        "message": message,
        "category": category
    }

# -------------------------
# Password validation
# -------------------------

def validate_password(password: str) -> str | None:
    if len(password) < 8:
        return "Password must be at least 8 characters long."

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."

    if not re.search(r"\d", password):
        return "Password must contain at least one number."

    if not re.search(r"[^\w\s]", password):
        return "Password must contain at least one special character."

    return None

AVATAR_COLOURS = [
    "#3f6fe5",
    "#7c4dff",
    "#00a896",
    "#f28c28",
    "#e05252",
    "#d94f9d",
    "#008cba",
    "#6b8e23",
]

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

    now = datetime.now(timezone.utc)
    if (
        user.last_active is None
        or now - user.last_active > timedelta(hours=1)
    ):
        user.last_active = now
        db.commit()
    return user


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
def movie(
    request: Request,
    movie_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    movie = get_movie(movie_id)
    providers = get_watch_providers(movie_id)

    watchlist_item = None

    if user:
        watchlist_item = (
            db.query(WatchlistItem)
            .filter(
                WatchlistItem.user_id == user.id,
                WatchlistItem.tmdb_id == movie_id,
                WatchlistItem.media_type == "movie"
            )
            .first()
        )

    return templates.TemplateResponse(
        request=request,
        name="movie.html",
        context={
            "request": request,
            "movie": movie,
            "poster": poster_url(movie.get("poster_path")),
            "backdrop": movie.get("backdrop_path"),
            "providers_html": build_providers_html(providers),
            "user": user,
            "watchlist_item": watchlist_item
        }
    )


# -------------------------
# TV PAGE
# -------------------------

@app.get("/tv/{tv_id}", response_class=HTMLResponse)
def tv(
    request: Request,
    tv_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    tv = get_tv_show(tv_id)
    providers = get_tv_watch_providers(tv_id)

    watchlist_item = None

    if user:
        watchlist_item = (
            db.query(WatchlistItem)
            .filter(
                WatchlistItem.user_id == user.id,
                WatchlistItem.tmdb_id == tv_id,
                WatchlistItem.media_type == "tv"
            )
            .first()
        )

    return templates.TemplateResponse(
        request=request,
        name="tv.html",
        context={
            "request": request,
            "tv": tv,
            "poster": poster_url(tv.get("poster_path")),
            "backdrop": tv.get("backdrop_path"),
            "providers_html": build_providers_html(providers),
            "user": user,
            "watchlist_item": watchlist_item
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
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    if not user:
        return RedirectResponse(
            url="/welcome?next=/watchlist&action=watchlist",
            status_code=303
        )

    watchlist_items = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == user.id)
        .order_by(WatchlistItem.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="watchlist.html",
        context={
            "request": request,
            "user": user,
            "watchlist": watchlist_items
        }
    )
    

@app.post("/watchlist/add")
def add_to_watchlist(
    request: Request,
    tmdb_id: int = Form(...),
    media_type: str = Form(...),
    title: str = Form(...),
    poster_path: str = Form(None),
    return_url: str = Form("/"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    if not user:
        return RedirectResponse(
            url="/login?next=" + request.headers.get("referer", "/"),
            status_code=303
        )

    existing = (
        db.query(WatchlistItem)
        .filter(
            WatchlistItem.user_id == user.id,
            WatchlistItem.tmdb_id == tmdb_id,
            WatchlistItem.media_type == media_type
        )
        .first()
    )

    if existing:
        set_flash(
            request,
            "Already in your watchlist.",
            "success"
            )
        return RedirectResponse(
            url=return_url,
            status_code=303
        )

    item = WatchlistItem(
        user_id=user.id,
        tmdb_id=tmdb_id,
        media_type=media_type,
        title=title,
        poster_path=poster_path,
        status="want_to_watch"
    )

    db.add(item)
    db.commit()

    set_flash(
    request,
    "Added to your watchlist.",
    "success"
)
    return RedirectResponse(
        url=return_url,
        status_code=303
    )
    
@app.post("/watchlist/remove")
def remove_from_watchlist(
    request: Request,
    tmdb_id: int = Form(...),
    media_type: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    if not user:
        return RedirectResponse(
            url="/welcome?next=/watchlist&action=watchlist",
            status_code=303
        )

    item = (
        db.query(WatchlistItem)
        .filter(
            WatchlistItem.user_id == user.id,
            WatchlistItem.tmdb_id == tmdb_id,
            WatchlistItem.media_type == media_type
        )
        .first()
    )

    if item:
        db.delete(item)
        db.commit()

        set_flash(
            request,
            "Removed from your watchlist.",
            "success"
            )
    return RedirectResponse(
        url=request.headers.get("referer", "/watchlist"),
        status_code=303
    )
@app.post("/watchlist/status")
def change_watchlist_status(
    request: Request,
    item_id: int = Form(...),
    status: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    if not user:
        return RedirectResponse(
            url="/welcome?next=/watchlist&action=watchlist",
            status_code=303
        )

    allowed_statuses = {
        "want_to_watch",
        "watching",
        "finished"
    }

    if status not in allowed_statuses:
        return RedirectResponse(
            url="/watchlist",
            status_code=303
        )

    item = (
        db.query(WatchlistItem)
        .filter(
            WatchlistItem.id == item_id,
            WatchlistItem.user_id == user.id
        )
        .first()
    )

    if item:
        item.status = status
        db.commit()

    return RedirectResponse(
        url="/watchlist",
        status_code=303
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
            url="/welcome?next=/profile&action=profile",
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

    registered = request.query_params.get("registered")
    next_url = request.query_params.get("next")
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "success": success,
            "error": error,
            "registered": registered,
            "next_url": next_url
        }
    )
@app.post("/login", response_class=HTMLResponse)
def login_user(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    next_url: str = Form(""),
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
    request.session["username"] = user.username
    request.session["avatar_colour"] = user.avatar_colour

    set_flash(
            request,
            f"Welcome to WatchFinder, {user.username}!",
            "success"
        )
    
    if next_url:
        return RedirectResponse(
            url=next_url,
            status_code=303
        )
    
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

    set_flash(
        request,
        "You've been logged out.",
        "success"
    )

    return RedirectResponse(
        url="/",
        status_code=303
    )

#-------------------------
# REGISTER PAGE
#------------------------
@app.get("/register", response_class=HTMLResponse)
def register(request: Request):

    next_url = request.query_params.get("next", "")
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "request": request,
            "next_url": next_url
        }
    )

@app.post("/register", response_class=HTMLResponse)
def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    next_url: str = Form(""),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    username = username.strip()
    email = email.strip().lower()
    
    password_error = validate_password(password)
    
    if password_error:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "request": request,
                "error": password_error,
                "username": username,
                "email": email,
                "next_url": next_url
            }
        )

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
                "email": email,
                "next_url": next_url
            }
        )

    hashed_password = hash_password(password)

    user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        avatar_colour=random.choice(AVATAR_COLOURS)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["avatar_colour"] = user.avatar_colour

    set_flash(
        request,
        f"Welcome to WatchFinder, {user.username}!",
        "success"
    )

    if next_url:
        return RedirectResponse(
            url=next_url,
            status_code=303
        )
    
    return RedirectResponse(
        url="/profile",
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
            url="/login?next=/settings",
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
    
# -------------------------
# CHANGE USERNAME
# -------------------------

@app.get("/settings/username", response_class=HTMLResponse)
def change_username_page(
    request: Request,
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(
            url="/login?next=/settings/username",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="settings_username.html",
        context={
            "request": request,
            "user": user
        }
    )


@app.post("/settings/username", response_class=HTMLResponse)
def change_username(
    request: Request,
    username: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(
            url="/login?next=/settings/username",
            status_code=303
        )

    username = username.strip()

    existing_user = (
        db.query(User)
        .filter(
            User.username == username,
            User.id != user.id
        )
        .first()
    )

    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="settings_username.html",
            context={
                "request": request,
                "user": user,
                "error": "That username is already taken."
            }
        )

    user.username = username
    request.session["username"] = username

    db.commit()

    set_flash(
        request,
        "Username updated successfully.",
        "success"
)
    return RedirectResponse(
        url="/settings",
        status_code=303
    )
    
# -------------------------
# CHANGE EMAIL
# -------------------------

@app.get("/settings/email", response_class=HTMLResponse)
def change_email_page(
    request: Request,
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(
            url="/login?next=/settings/email",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="settings_email.html",
        context={
            "request": request,
            "user": user
        }
    )


@app.post("/settings/email", response_class=HTMLResponse)
def change_email(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(
            url="/login?next=/settings/email",
            status_code=303
        )

    email = email.strip().lower()

    existing_user = (
        db.query(User)
        .filter(
            User.email == email,
            User.id != user.id
        )
        .first()
    )

    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="settings_email.html",
            context={
                "request": request,
                "user": user,
                "error": "That email address is already registered."
            }
        )

    user.email = email

    db.commit()

    set_flash(
        request,
        "Email updated successfully.",
        "success"
)
    
    return RedirectResponse(
        url="/settings",
        status_code=303
    )

# -------------------------
# CHANGE PASSWORD
# -------------------------

@app.get("/settings/password", response_class=HTMLResponse)
def change_password_page(
    request: Request,
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(
            url="/login?next=/settings/password",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="settings_password.html",
        context={
            "request": request,
            "user": user
        }
    )


@app.post("/settings/password", response_class=HTMLResponse)
def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(
            url="/login?next=/settings/password",
            status_code=303
        )

    if not verify_password(current_password, user.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="settings_password.html",
            context={
                "request": request,
                "user": user,
                "error": "Your current password is incorrect."
            }
        )

    if new_password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="settings_password.html",
            context={
                "request": request,
                "user": user,
                "error": "The new passwords do not match."
            }
        )

    user.password_hash = hash_password(new_password)

    db.commit()

    set_flash(
        request,
        "Password updated successfully.",
        "success"
    )

    return RedirectResponse(
        url="/settings",
        status_code=303
    )

@app.get("/settings/avatar", response_class=HTMLResponse)
def avatar_settings(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse("/login?next=/settings/avatar")

    return templates.TemplateResponse(
        request=request,
        name="settings_avatar.html",
        context={
            "user": user,
            "avatar_colours": AVATAR_COLOURS
        }
    )


@app.post("/settings/avatar")
def update_avatar(
    request: Request,
    colour: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_current_user(request, db)

    if not user:
        return RedirectResponse("/login?next=/settings/avatar")

    if colour not in AVATAR_COLOURS:
        raise HTTPException(status_code=400, detail="Invalid avatar colour")

    user.avatar_colour = colour
    db.commit()

    request.session["avatar_colour"] = colour

    return RedirectResponse(
        "/settings/avatar",
        status_code=303
    )
  
#-------------------------
# INSTALL PAGE 
#------------------------
@app.get("/install", response_class=HTMLResponse)
def install_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="install.html",
        context={
            "request": request
        }
    )
    
# -------------------------
# ACCOUNT WELCOME PAGE
# -------------------------
@app.get("/welcome", response_class=HTMLResponse)
def welcome(request: Request):

    next_url = request.query_params.get("next", "/")
    action = request.query_params.get("action", "account")

    messages = {
        "watchlist": {
            "title": "Build your watchlist",
            "message": (
                "Create an account to save movies and TV shows "
                "you want to watch."
            )
        },
        "profile": {
            "title": "Access your profile",
            "message": (
                "Create an account or log in to view and manage "
                "your WatchFinder profile."
            )
        },
        "account": {
            "title": "Join WatchFinder",
            "message": (
                "Create an account to save your favourite movies "
                "and TV shows."
            )
        }
    }

    content = messages.get(action, messages["account"])

    return templates.TemplateResponse(
        request=request,
        name="welcome.html",
        context={
            "request": request,
            "next_url": next_url,
            "title": content["title"],
            "message": content["message"]
        }
    )
       
#-------------------------
# health check endpoints
#------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-health")
def db_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "error", "database": "unavailable"}