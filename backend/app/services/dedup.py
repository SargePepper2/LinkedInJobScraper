"""Job deduplication — fingerprint hashing and fuzzy description matching."""

import hashlib
import logging
import re

from sqlalchemy.orm import Session

from app.models.job import Job

logger = logging.getLogger(__name__)


def _normalize(text: str | None) -> str:
    """Lowercase, strip whitespace, collapse multiple spaces."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip().lower())


def generate_fingerprint(title: str, company: str | None, location: str | None) -> str:
    """Create a SHA-256 hex digest (first 64 chars) from normalized title+company+location."""
    key = "|".join([_normalize(title), _normalize(company), _normalize(location)])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def _fuzzy_description_match(desc_a: str, desc_b: str, chars: int = 200) -> bool:
    """Compare first N chars of two descriptions after normalization."""
    a = _normalize(desc_a)[:chars]
    b = _normalize(desc_b)[:chars]
    return a == b


def is_duplicate(
    db: Session,
    title: str,
    company: str | None,
    location: str | None,
    description: str = "",
) -> tuple[bool, str]:
    """Check if a job already exists.

    Returns (is_dup, fingerprint).
    First checks by fingerprint hash. If no fingerprint match, falls back to
    fuzzy description comparison against jobs with the same title.
    """
    fp = generate_fingerprint(title, company, location)

    # Exact fingerprint match
    existing = db.query(Job).filter(Job.fingerprint == fp).first()
    if existing:
        logger.info("Duplicate detected (fingerprint): '%s' at '%s' — skipping", title, company)
        return True, fp

    # Fuzzy description fallback: find jobs with same normalized title
    if description:
        norm_title = _normalize(title)
        candidates = db.query(Job).filter(Job.title.ilike(f"%{norm_title}%")).limit(50).all()
        for candidate in candidates:
            if _fuzzy_description_match(description, candidate.description):
                logger.info(
                    "Duplicate detected (fuzzy desc): '%s' matches job id=%d — skipping",
                    title,
                    candidate.id,
                )
                return True, fp

    return False, fp
