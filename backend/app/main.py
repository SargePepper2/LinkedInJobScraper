from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import analysis, jobs, profile, skills

app = FastAPI(
    title="LinkedIn Job Skills Analyzer",
    description="Scrape job postings, extract skills, and get career intelligence",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
