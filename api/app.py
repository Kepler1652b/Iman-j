from fastapi import FastAPI
from .v1.routes import router
import os
from database.db import create_db
from contextlib import asynccontextmanager


DB_PATH = 'C:/Users/mfoad/OneDrive/Documents/Codes/Karlancer/Iman-J-Telegram/movies.db'



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


