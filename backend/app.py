import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.api.routes import router

from pathlib import Path

# Load environment variables explicitly from backend/.env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="AI Resume Screening API")

# Configure CORS
cors_env = os.getenv("CORS_ORIGINS", "").strip()
if cors_env:
    origins = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
else:
    origins = [
        "http://localhost:5173",  # React frontend URL
        "https://resume-screener-frntend.onrender.com",  # Production frontend URL
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Register API routes
app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

