import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).parent.parent  # one level up
ENV_PATH = BASE_DIR / ".env"


if not ENV_PATH.exists():
    raise FileNotFoundError(f".env file not found at {ENV_PATH}")

load_dotenv(dotenv_path=ENV_PATH)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in environment variables.")
CHANNEL_ID = os.getenv("CHANNEL_ID")
if not CHANNEL_ID:
    raise RuntimeError("CHANNEL_ID is not set in environment variables.")
ADMINS = os.getenv("ADMINS")
if not ADMINS:
    raise RuntimeError("NO admin set . add at least one admin")



DB_PATH = os.getenv("DB_PATH", BASE_DIR / "movie.db")
DB_PATH = str(DB_PATH)

