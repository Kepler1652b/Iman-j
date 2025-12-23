from fastapi import FastAPI, Request, HTTPException
from .v1.routes import router
from database.db import create_db
from contextlib import asynccontextmanager
from pathlib import Path
import os
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


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





# Global exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors and return readable JSON
    """
    errors = []
    
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_type = error["type"]
        
        # Create readable error message
        if error_type == "missing":
            readable_message = f"Field '{field}' is required and cannot be empty"
        elif error_type == "type_error.none.not_allowed":
            readable_message = f"Field '{field}' cannot be null"
        elif error_type == "value_error":
            readable_message = f"Field '{field}' has invalid value: {message}"
        else:
            readable_message = f"Field '{field}': {message}"
        
        errors.append({
            "field": field,
            "message": readable_message,
            "type": error_type
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "One or more fields are invalid",
            "details": errors
        }
    )


# Optional: Handle generic exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Catch any unhandled exceptions and return readable error
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )


# Optional: Handle Pydantic validation errors
@app.exception_handler(ValidationError)
async def pydantic_exception_handler(request: Request, exc: ValidationError):
    """
    Handle Pydantic model validation errors
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid data provided",
            "details": exc.errors()
        }
    )
