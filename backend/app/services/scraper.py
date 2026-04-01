"""Multi-source job scraping framework."""

from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.models.job import Job, ScrapeRun, SkillOccurrence
from app.models.skill import Skill, SkillCategory
from app.services.dedup import generate_fingerprint, is_duplicate
from app.services.extractor import SkillExtractor

logger = logging.getLogger(__name__)


@dataclass
class RawJob:
    """Standardized job representation returned by all scrapers."""

    title: str
    company: str | None
    location: str | None
    description: str
    source: str
    url: str | None


class JobScraper(ABC):
    """Base class for all job board scrapers."""

    source_name: str = "unknown"

    @abstractmethod
    def scrape(self, query: str, location: str | None = None, limit: int = 25) -> list[RawJob]:
        """Scrape jobs matching *query*. Return up to *limit* results."""
        ...


class HNHiringScraper(JobScraper):
    """Scrape Hacker News 'Ask HN: Who is Hiring?' threads via the Algolia API."""

    source_name = "hackernews"
    _HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"

    def scrape(self, query: str, location: str | None = None, limit: int = 25) -> list[RawJob]:
        # Find the latest "Who is Hiring" thread
        params = {
            "query": "Ask HN: Who is hiring",
            "tags": "story",
            "hitsPerPage": 1,
        }
        try:
            resp = httpx.get(self._HN_SEARCH_URL, params=params, timeout=15)
            resp.raise_for_status()
            hits = resp.json().get("hits", [])
        except Exception:
            logger.exception("Failed to find HN hiring thread")
            return []

        if not hits:
            return []

        story_id = hits[0]["objectID"]

        # Fetch comments (job posts) for that thread
        comments_url = f"https://hn.algolia.com/api/v1/search?tags=comment,story_{story_id}&hitsPerPage={limit * 3}"
        try:
            resp = httpx.get(comments_url, timeout=30)
            resp.raise_for_status()
            comments = resp.json().get("hits", [])
        except Exception:
            logger.exception("Failed to fetch HN comments")
            return []

        query_lower = query.lower()
        jobs: list[RawJob] = []

        for comment in comments:
            text = comment.get("comment_text", "") or ""
            # Strip HTML tags
            plain = re.sub(r"<[^>]+>", " ", text)
            plain = re.sub(r"\s+", " ", plain).strip()

            if not plain or (query_lower and query_lower not in plain.lower()):
                continue

            # Try to parse "Company | Role | Location" pattern common in HN posts
            first_line = plain.split("\n")[0] if "\n" in plain else plain[:200]
            parts = [p.strip() for p in first_line.split("|")]

            company = parts[0] if len(parts) >= 1 else None
            title = parts[1] if len(parts) >= 2 else "HN Posting"
            loc = parts[2] if len(parts) >= 3 else None

            jobs.append(
                RawJob(
                    title=title[:300],
                    company=company[:200] if company else None,
                    location=loc[:200] if loc else None,
                    description=plain[:5000],
                    source="hackernews",
                    url=f"https://news.ycombinator.com/item?id={comment.get('objectID', '')}",
                )
            )

            if len(jobs) >= limit:
                break

        return jobs


class IndeedScraper(JobScraper):
    """Placeholder for Indeed scraping — not yet implemented."""

    source_name = "indeed"

    def scrape(self, query: str, location: str | None = None, limit: int = 25) -> list[RawJob]:
        # TODO: Implement Indeed scraping with proper auth/API
        raise NotImplementedError("Indeed scraper is not yet implemented")


class LinkedInScraper(JobScraper):
    """Placeholder for LinkedIn scraping — not yet implemented."""

    source_name = "linkedin"

    def scrape(self, query: str, location: str | None = None, limit: int = 25) -> list[RawJob]:
        # TODO: Implement LinkedIn scraping with proper auth/API
        raise NotImplementedError("LinkedIn scraper is not yet implemented")


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

SCRAPERS: dict[str, type[JobScraper]] = {
    "hn": HNHiringScraper,
    "indeed": IndeedScraper,
    "linkedin": LinkedInScraper,
}


def get_scraper(source: str) -> JobScraper:
    cls = SCRAPERS.get(source)
    if not cls:
        raise ValueError(f"Unknown scraper source: {source}")
    return cls()


# ---------------------------------------------------------------------------
# Import pipeline: scrape -> dedup -> persist
# ---------------------------------------------------------------------------

_extractor: SkillExtractor | None = None


def _get_extractor() -> SkillExtractor:
    global _extractor
    if _extractor is None:
        _extractor = SkillExtractor()
    return _extractor


def _ensure_skill(db: Session, name: str, category: str) -> Skill:
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


def run_scrape_pipeline(
    db: Session,
    source: str,
    query: str,
    location: str | None = None,
    limit: int = 25,
) -> dict:
    """Scrape jobs from *source*, dedup, extract skills, persist."""
    scraper = get_scraper(source)

    run = ScrapeRun(source=scraper.source_name, query=query, status="running")
    db.add(run)
    db.flush()

    raw_jobs = scraper.scrape(query, location=location, limit=limit)

    imported = 0
    skipped = 0
    extractor = _get_extractor()

    for rj in raw_jobs:
        dup, fp = is_duplicate(db, rj.title, rj.company, rj.location, rj.description)
        if dup:
            skipped += 1
            continue

        job = Job(
            title=rj.title,
            company=rj.company,
            location=rj.location,
            description=rj.description,
            source=rj.source,
            source_url=rj.url,
            fingerprint=fp,
            scrape_run_id=run.id,
        )
        db.add(job)
        db.flush()

        extracted = extractor.extract(rj.description)
        for es in extracted:
            skill = _ensure_skill(db, es.name, es.category)
            occ = SkillOccurrence(
                job_id=job.id,
                skill_id=skill.id,
                context_snippet=es.context[:500] if es.context else None,
            )
            db.add(occ)

        imported += 1

    run.completed_at = datetime.now(timezone.utc)
    run.jobs_found = imported
    run.status = "completed"
    db.commit()

    return {
        "scrape_run_id": run.id,
        "source": scraper.source_name,
        "jobs_found": len(raw_jobs),
        "imported": imported,
        "skipped_duplicates": skipped,
    }
