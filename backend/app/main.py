from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routers import auth, products
from app.database import engine, Base
from app.models import user, product
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis
from sqlalchemy import text
from app.limiter import limiter
import logging
import time

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Vastarion Hunter",
    description="Price tracking and deal hunting API",
    version="1.0.0"
)

app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please slow down."}
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vastarion-hunter")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = round(time.time() - start_time, 3)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}s)")
    return response

app.include_router(auth.router)
app.include_router(products.router)

@app.get("/")
@limiter.limit("10/minute")
def root(request: Request):
    return {"message": "Vastarion Hunter API is running!"}

@app.get("/health")
def health():
    status = {"api": "healthy"}

    try:
        from app.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        status["database"] = "healthy"
    except Exception as e:
        status["database"] = f"unhealthy: {str(e)}"

    try:
        r = redis.from_url("redis://redis:6379/0")
        r.ping()
        status["redis"] = "healthy"
    except Exception as e:
        status["redis"] = f"unhealthy: {str(e)}"

    return status