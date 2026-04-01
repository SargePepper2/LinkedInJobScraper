"""Import job descriptions from paste, CSV, or JSON."""

import csv
import io
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.job import Job, ScrapeRun, SkillOccurrence
from app.models.skill import Skill, SkillCategory
from app.services.dedup import generate_fingerprint, is_duplicate
from app.services.extractor import SkillExtractor

logger = logging.getLogger(__name__)

_extractor: SkillExtractor | None = None


def _get_extractor() -> SkillExtractor:
    global _extractor
    if _extractor is None:
        _extractor = SkillExtractor()
    return _extractor


def _ensure_skill(db: Session, name: str, category: str) -> Skill:
    """Get or create a skill record."""
    skill = db.query(Skill).filter(Skill.name == name).first()
    if not skill:
        try:
            cat = SkillCategory(category)
        except ValueError:
            cat = SkillCategory.OTHER
        skill = Skill(name=name, category=cat, aliases=[])
        db.add(skill)
        db.flush()
    return skill


def import_text(
    db: Session, text: str, title: str = "Untitled", company: str | None = None
) -> Job | None:
    """Import a single pasted job description. Returns None if duplicate."""
    dup, fp = is_duplicate(db, title, company, None, text)
    if dup:
        logger.info("Skipping duplicate import: '%s' at '%s'", title, company)
        return None

    job = Job(
        title=title,
        company=company,
        description=text,
        source="manual",
        fingerprint=fp,
    )
    db.add(job)
    db.flush()

    extractor = _get_extractor()
    extracted = extractor.extract(text)

    for es in extracted:
        skill = _ensure_skill(db, es.name, es.category)
        occ = SkillOccurrence(
            job_id=job.id,
            skill_id=skill.id,
            context_snippet=es.context[:500] if es.context else None,
        )
        db.add(occ)

    db.commit()
    return job


def import_csv(db: Session, csv_content: str) -> list[Job]:
    """Import jobs from CSV. Expected columns: title, company, location, description."""
    reader = csv.DictReader(io.StringIO(csv_content))
    jobs = []

    run = ScrapeRun(
        source="csv_import",
        query=None,
        status="running",
    )
    db.add(run)
    db.flush()

    for row in reader:
        description = row.get("description", "")
        if not description.strip():
            continue

        row_title = row.get("title", "Untitled")
        row_company = row.get("company")
        row_location = row.get("location")

        dup, fp = is_duplicate(db, row_title, row_company, row_location, description)
        if dup:
            logger.info("CSV import: skipping duplicate '%s' at '%s'", row_title, row_company)
            continue

        job = Job(
            title=row_title,
            company=row_company,
            location=row_location,
            description=description,
            source="csv",
            fingerprint=fp,
            scrape_run_id=run.id,
        )
        db.add(job)
        db.flush()

        extractor = _get_extractor()
        extracted = extractor.extract(description)

        for es in extracted:
            skill = _ensure_skill(db, es.name, es.category)
            occ = SkillOccurrence(
                job_id=job.id,
                skill_id=skill.id,
                context_snippet=es.context[:500] if es.context else None,
            )
            db.add(occ)

        jobs.append(job)

    run.completed_at = datetime.now(timezone.utc)
    run.jobs_found = len(jobs)
    run.status = "completed"
    db.commit()

    return jobs
