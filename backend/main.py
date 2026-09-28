import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.routes.incidents import router as incidents_router
from backend.routes.dashboard import router as dashboard_router

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
ENV_PATH = BASE_DIR / ".env"

# Load environment variables
load_dotenv(dotenv_path=ENV_PATH, override=True)

app = FastAPI(
    title="Incident Response Agent API",
    description="AI-Powered Incident Response Agent with Hindsight Persistent Memory",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(incidents_router)
app.include_router(dashboard_router)

# Health & Status API Endpoints
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint"""
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    from backend.database import db_get_stats
    return {
        "status": "healthy",
        "service": "Incident Response Agent",
        "version": "1.0.0",
        "database": db_get_stats(),
        "hindsight_configured": bool(os.getenv("HINDSIGHT_API_KEY")),
        "llm_configured": bool(os.getenv("GROQ_API_KEY"))
    }

@app.get("/api/database/status", tags=["Database"])
async def database_status():
    """Returns SQLite relational database statistics and record counts"""
    from backend.database import db_get_stats
    return db_get_stats()

@app.get("/api/status", tags=["Health"])
async def system_status():
    """Returns runtime configuration status and active service flags"""
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    from backend.database import db_get_stats
    return {
        "status": "online",
        "database": db_get_stats(),
        "hindsight": {
            "api_url": os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.vectorize.io"),
            "bank_id": os.getenv("HINDSIGHT_BANK_ID", "sentinelmind-soc-bank"),
            "is_configured": bool(os.getenv("HINDSIGHT_API_KEY"))
        },
        "llm": {
            "model": os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
            "is_configured": bool(os.getenv("GROQ_API_KEY"))
        }
    }

# Mount Frontend Static Assets
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    # Serve HTML Pages
    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    @app.get("/dashboard", include_in_schema=False)
    async def serve_dashboard():
        return FileResponse(str(FRONTEND_DIR / "dashboard.html"))

    @app.get("/incident", include_in_schema=False)
    async def serve_incident():
        return FileResponse(str(FRONTEND_DIR / "incident.html"))

    @app.get("/history", include_in_schema=False)
    async def serve_history():
        return FileResponse(str(FRONTEND_DIR / "history.html"))

    @app.get("/analysis", include_in_schema=False)
    async def serve_analysis():
        return FileResponse(str(FRONTEND_DIR / "analysis.html"))

    @app.get("/memory", include_in_schema=False)
    async def serve_memory():
        return FileResponse(str(FRONTEND_DIR / "memory.html"))

    @app.get("/reports", include_in_schema=False)
    async def serve_reports():
        return FileResponse(str(FRONTEND_DIR / "reports.html"))

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
