from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import sources, jobs, skills, roles, market, quality

app = FastAPI(
    title="Sri Lanka IT Talent Intelligence API",
    description="API for the Sri Lanka IT Talent Intelligence Platform",
    version="0.1.0"
)

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
