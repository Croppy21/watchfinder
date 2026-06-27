import os
from dotenv import load_dotenv

load_dotenv()

TMDB_READ_ACCESS_TOKEN = (
    os.getenv("TMDB_READ_ACCESS_TOKEN", "")
    .strip()
    .replace("\n", "")
    .replace("\r", "")
)