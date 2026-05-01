import logging
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

# Load .env from project root regardless of which directory uvicorn is run from
from pathlib import Path
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

from tools.sql_tools import get_all_movies
from tools.csv_tools import analyze_movies
from services.ai_service import run_agent
from security import verify_api_key, validate_query, add_security_headers
from db import load_data

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Secure AI Insights Assistant")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Security headers middleware ───────────────────────────────────────────────
app.middleware("http")(add_security_headers)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Dev mode (no API_KEY set): allow all origins so file:// and any local port works
# Production (API_KEY set): restrict to ALLOWED_ORIGINS env var
_api_key_enabled = bool(os.getenv("API_KEY"))
if _api_key_enabled:
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    logger.info("Starting up — loading data into SQLite")
    load_data()
    logger.info("Startup complete")

# ── Request model ─────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Secure AI Insights Assistant is running"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "hf_api_key_present": bool(os.getenv("HF_API_KEY")),
        "api_key_enabled": bool(os.getenv("API_KEY")),
    }


@app.get("/movies", dependencies=[Depends(verify_api_key)])
def fetch_movies():
    try:
        data = get_all_movies()
        if isinstance(data, dict) and "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])
        return {"count": len(data), "data": data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("GET /movies error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", dependencies=[Depends(verify_api_key)])
@limiter.limit("30/minute")
def chat(request: Request, body: ChatRequest):
    try:
        clean_query = validate_query(body.query)
        logger.info("POST /chat — query: %s", clean_query[:80])
        response = run_agent(clean_query)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error("POST /chat error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", dependencies=[Depends(verify_api_key)])
def ingest():
    """Reload all CSV files into SQLite. Call this after updating any CSV."""
    try:
        logger.info("POST /ingest — reloading all CSV tables")
        load_data()
        logger.info("Ingest complete")
        return {"status": "ok", "message": "All CSV tables reloaded into SQLite"}
    except Exception as e:
        logger.error("POST /ingest error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chart", dependencies=[Depends(verify_api_key)])
def get_chart():
    try:
        data = analyze_movies()
        if isinstance(data, dict) and "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])

        genres = data["genre_distribution"]
        plt.figure()
        plt.bar(genres.keys(), genres.values(), color="#2563eb")
        plt.title("Genre Distribution")
        plt.xlabel("Genre")
        plt.ylabel("Movie Count")
        plt.tight_layout()

        file_path = "chart.png"
        plt.savefig(file_path)
        plt.close()
        logger.info("GET /chart — chart generated")
        return FileResponse(file_path, media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("GET /chart error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
