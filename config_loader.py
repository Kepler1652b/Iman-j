import yaml
from pathlib import Path
from dotenv import load_dotenv
import os

CONFIG_FILE = Path(__file__).parent / "../config.yaml"
BASE_DIR = Path(__file__).parent.parent  # one level up
ENV_PATH = BASE_DIR / ".env"

def load_config(file_path=CONFIG_FILE):
    """Load YAML configuration and return as dictionary."""
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Load once
config = load_config()

DEFAULT_LOCALE = config.get("default_locale", "fa")
LOCALES = config.get("locales", {})



if not ENV_PATH.exists():
    raise FileNotFoundError(f".env file not found at {ENV_PATH}")

load_dotenv(dotenv_path=ENV_PATH)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in environment variables.")

DB_PATH = os.getenv("DB_PATH", BASE_DIR / "voting.db")
DB_PATH = str(DB_PATH)

