import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from backend.app.config import settings
from backend.app.database.database import init_db
from backend.app.api.routes_reports import router as reports_router
from backend.app.api.routes_chat import router as chat_router
from backend.app.api.routes_crops import router as crops_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Understand Your Soil. Backed by Evidence. Agentic RAG & ML Crop Suitability System.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(reports_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
app.include_router(crops_router, prefix=settings.API_V1_PREFIX)

@app.get("/api/health", tags=["system"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "llm_provider": settings.LLM_PROVIDER,
        "max_retries": settings.MAX_RETRIES
    }

# Mount static frontend if frontend/dist exists (for Render & production Docker container)
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
assets_dir = frontend_dist / "assets"

if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

if frontend_dist.exists():
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        target = frontend_dist / full_path
        if target.is_file():
            return FileResponse(target)
        return FileResponse(frontend_dist / "index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=False)
