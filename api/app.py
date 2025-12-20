from fastapi import FastAPI
from .v1.routes import router
import os
from database.db import create_db
from contextlib import asynccontextmanager


from pathlib import Path

# Get project root (assuming script is in a subdirectory)
BASE_DIR = Path(__file__).parent.parent.resolve()

# Database in project root
DB_PATH = BASE_DIR / 'movies.db'


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        create_db()
    else:
        print(f"Database already exists at {DB_PATH}")
    
    yield  # Application runs here
    
    # Shutdown: Add any cleanup code here if needed
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)
app.include_router(router,prefix='/api')


