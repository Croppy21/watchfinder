import os
from dotenv import load_dotenv

load_dotenv()

TMDB_READ_ACCESS_TOKEN = (
    os.getenv("TMDB_READ_ACCESS_TOKEN", "")
    .strip()
    .replace("\n", "")
    .replace("\r", "")
)
if not TMDB_READ_ACCESS_TOKEN:
    raise RuntimeError("TMDB_READ_ACCESS_TOKEN is missing or not loaded")