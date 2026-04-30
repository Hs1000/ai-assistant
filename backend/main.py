from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import matplotlib
from fastapi.middleware.cors import CORSMiddleware

# Use non-GUI backend for server environments/threads.
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

# Import tools and services
from tools.sql_tools import get_all_movies
from tools.csv_tools import analyze_movies
from services.ai_service import run_agent
from db import load_data

# -------------------------------
# INITIALIZE APP
# -------------------------------
app = FastAPI(title="AI Insights Assistant (Hugging Face)")

# -------------------------------
# CORS (for frontend)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# AUTO DB INITIALIZATION
# -------------------------------
@app.on_event("startup")
def startup_event():
    load_data()

# -------------------------------
# REQUEST MODEL
# -------------------------------
class ChatRequest(BaseModel):
    query: str


# -------------------------------
# ROOT ENDPOINT
# -------------------------------
@app.get("/")
def home():
    return {"message": "Backend running successfully 🚀"}


# -------------------------------
# HEALTH CHECK
# -------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "hf_api_key_present": bool(os.getenv("HF_API_KEY"))
    }


# -------------------------------
# SQL DATA ENDPOINT
# -------------------------------
@app.get("/movies")
def fetch_movies():
    try:
        data = get_all_movies()

        # Handle DB errors
        if isinstance(data, dict) and "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])

        return {
            "count": len(data),
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# CHAT ENDPOINT (AI AGENT)
# -------------------------------
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        print("QUERY RECEIVED:", request.query)

        response = run_agent(request.query)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# CHART ENDPOINT (Visualization)
# -------------------------------
@app.get("/chart")
def get_chart():
    try:
        data = analyze_movies()

        # Handle CSV errors
        if isinstance(data, dict) and "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])

        genres = data["genre_distribution"]

        # Create chart
        plt.figure()
        plt.bar(genres.keys(), genres.values())
        plt.title("Genre Distribution")
        plt.xlabel("Genre")
        plt.ylabel("Movie Count")

        file_path = "chart.png"
        plt.savefig(file_path)
        plt.close()

        return FileResponse(file_path, media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))