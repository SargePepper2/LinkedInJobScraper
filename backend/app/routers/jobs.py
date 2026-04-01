from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.job import Job
from app.services.importer import import_csv, import_text

router = APIRouter()


class PasteJobRequest(BaseModel):
    title: str = "Untitled"
    company: str | None = None
    description: str


class JobResponse(BaseModel):
    id: int
    title: str
    company: str | None
    location: str | None
    source: str
    skills_found: int

    model_config = {"from_attributes": True}


@router.post("/import/paste", response_model=JobResponse)
def paste_job(req: PasteJobRequest, db: Session = Depends(get_db)):
    """Import a single job description by pasting text."""
    job = import_text(db, req.description, req.title, req.company)
    if job is None:
        raise HTTPException(409, "Duplicate job detected — skipped")
    return JobResponse(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        source=job.source,
        skills_found=len(job.skill_occurrences),
    )


@router.post("/import/csv")
def upload_csv(file: UploadFile, db: Session = Depends(get_db)):
    """Import jobs from a CSV file."""
    content = file.file.read().decode("utf-8")
    jobs = import_csv(db, content)
    return {"imported": len(jobs)}


@router.get("/", response_model=list[JobResponse])
def list_jobs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List imported jobs."""
    jobs = db.query(Job).order_by(Job.scraped_at.desc()).offset(skip).limit(limit).all()
    return [
        JobResponse(
            id=j.id,
            title=j.title,
            company=j.company,
            location=j.location,
            source=j.source,
            skills_found=len(j.skill_occurrences),
        )
        for j in jobs
    ]
