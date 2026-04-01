"""Router for multi-source job scraping."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.scraper import SCRAPERS, run_scrape_pipeline

router = APIRouter()


class ScrapeRequest(BaseModel):
    source: str = Field(..., pattern="^(hn|indeed|linkedin|remoteok|weworkremotely|builtin)$")
    query: str
    location: str | None = None
    limit: int = Field(25, ge=1, le=200)


class ScrapeResponse(BaseModel):
    scrape_run_id: int
    source: str
    jobs_found: int
    imported: int
    skipped_duplicates: int


@router.get("/sources")
def list_sources():
    """Return available scraper source names."""
    return {"sources": sorted(SCRAPERS.keys())}


@router.post("/run", response_model=ScrapeResponse)
def scrape_run(req: ScrapeRequest, db: Session = Depends(get_db)):
    """Kick off a scrape from the specified source."""
    try:
        result = run_scrape_pipeline(
            db,
            source=req.source,
            query=req.query,
            location=req.location,
            limit=req.limit,
        )
    except NotImplementedError as exc:
        raise HTTPException(501, str(exc))
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    return ScrapeResponse(**result)
