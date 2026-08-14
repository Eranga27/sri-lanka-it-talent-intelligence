import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routers import sources, jobs, skills, roles, market, quality

logger = logging.getLogger("api")

app = FastAPI(
    title="Sri Lanka IT Talent Intelligence API",
    description="API for the Sri Lanka IT Talent Intelligence Platform",
    version="0.1.0"
)

# Configurable CORS origins for production security
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler preventing internal Python stack traces or file paths
    from leaking to client responses.
    """
    logger.error("Unhandled internal API exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "We couldn't refresh or load the requested market data. Internal server error."},
    )

@app.get("/api/health", tags=["System"])
async def health_check():
    return {"status": "ok", "message": "Sri Lanka IT Talent Intelligence API is running"}

app.include_router(sources.router, prefix="/api/sources", tags=["Sources"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
app.include_router(roles.router, prefix="/api/roles", tags=["Roles"])
app.include_router(market.router, prefix="/api/market", tags=["Market Intelligence"])
app.include_router(quality.router, prefix="/api/data-quality", tags=["Data Quality"])
