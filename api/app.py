from fastapi import FastAPI, Request, HTTPException
from .v1.routes import router
from database.db import create_db
from contextlib import asynccontextmanager
from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = BASE_DIR / "movies.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        create_db()
    else:
        print(f"Database already exists at {DB_PATH}")
    yield
    print("Shutting down...")


# ✅ SINGLE FastAPI instance
app = FastAPI(lifespan=lifespan)


# ✅ PROXY GUARD (ADD HERE)
from fastapi.responses import JSONResponse

@app.middleware("http")
async def proxy_guard(request: Request, call_next):
    if request.headers.get("X-Internal-Proxy") != "true":
        return JSONResponse(status_code=403, content={"detail": "Forbidden"})
    return await call_next(request)

# ✅ HEALTH CHECK (OPTIONAL BUT GOOD)
@app.get("/")
async def health():
    return {"status": "ok"}


# ✅ ROUTES
app.include_router(router, prefix="/api")
