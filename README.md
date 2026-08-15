# WatchFinder

WatchFinder helps users find where movies and TV shows are available to stream.

Built with Flask and the TMDB API, the app allows users to search for titles and view their available streaming providers in one place.

## Live Demo
https://watchfinder-app.onrender.com/
## Why I built this

I created WatchFinder to improve my skills in:

- Python
- API integration
- HTML, CSS and JavaScript
- Responsive web design
- Git and GitHub
- mobile UI design

## Features

- Search for movies and TV shows
- Autocomplete suggestions
- View streaming providers
- Mobile-friendly design

## Tech Stack

- Python
- FastAPI
- HTML/CSS
- JavaScript
- TMDB API

---

## Run locally

Clone the repository:

```bash
git clone https://github.com/Croppy21/watchfinder.git
cd watchfinder
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
TMDB_API_KEY=your_api_key_here
```

Run the app:

```bash
uvicorn app:app --host 0.0.0.0 --reload
```

Open on your computer:

```text
http://127.0.0.1:8000
```

To view on a mobile device:

1. Make sure your phone and computer are connected to the same Wi-Fi network.
2. Find your computer's local IP address:
   - Windows: Run `ipconfig` and look for the IPv4 Address.
   - Mac/Linux: Run `ifconfig` or `ip addr`.
3. Open this on your phone:

```text
http://YOUR_LOCAL_IP:8000
```

Example:

```text
http://192.168.1.25:8000
```

Movie and TV data is provided by TMDB.
