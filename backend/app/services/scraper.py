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


class RemoteOKScraper(JobScraper):
    """Scrape RemoteOK via their public JSON API."""

    source_name = "remoteok"
    _API_URL = "https://remoteok.com/api"

    def scrape(self, query: str, location: str | None = None, limit: int = 25) -> list[RawJob]:
        headers = {
            "User-Agent": "SkillScope/1.0 (job-skill-analytics; contact@skillscope.dev)",
        }
        try:
            resp = httpx.get(self._API_URL, headers=headers, timeout=20)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            logger.exception("Failed to fetch RemoteOK API")
            return []

        # The first element in the response is a metadata/legal notice object; skip it
        if data and isinstance(data, list) and isinstance(data[0], dict) and "id" not in data[0]:
            data = data[1:]

        query_lower = query.lower() if query else ""
        jobs: list[RawJob] = []

        for item in data:
            position = item.get("position", "") or ""
            description = item.get("description", "") or ""

            if query_lower and query_lower not in position.lower() and query_lower not in description.lower():
                continue

            company = item.get("company", "") or None
            loc = item.get("location", "") or "Remote"
            tags = item.get("tags", []) or []
            url = item.get("url", "") or f"https://remoteok.com/remote-jobs/{item.get('id', '')}"

            # Build a richer description from tags + description
            tag_line = f"Tags: {', '.join(tags)}\n\n" if tags else ""
            full_desc = f"{tag_line}{description}"

            jobs.append(
                RawJob(
                    title=position[:300],
                    company=company[:200] if company else None,
                    location=loc[:200],
                    description=full_desc[:5000],
                    source="remoteok",
                    url=url,
                )
            )

            if len(jobs) >= limit:
                break

        return jobs


class WeWorkRemotelyScraper(JobScraper):
    """Scrape We Work Remotely via their public RSS feeds."""

    source_name = "weworkremotely"
    _FEEDS = [
        "https://weworkremotely.com/categories/remote-programming-jobs.rss",
        "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
    ]

    def scrape(self, query: str, location: str | None = None, limit: int = 25) -> list[RawJob]:
        import xml.etree.ElementTree as ET

        query_lower = query.lower() if query else ""
        jobs: list[RawJob] = []

        for feed_url in self._FEEDS:
            if len(jobs) >= limit:
                break

            try:
                resp = httpx.get(
                    feed_url,
                    headers={"User-Agent": "SkillScope/1.0"},
                    timeout=15,
                )
                resp.raise_for_status()
            except Exception:
                logger.exception("Failed to fetch WWR feed: %s", feed_url)
                continue

            try:
                root = ET.fromstring(resp.text)
            except ET.ParseError:
                logger.exception("Failed to parse WWR RSS XML from %s", feed_url)
                continue

            for item in root.findall(".//item"):
                if len(jobs) >= limit:
                    break

                raw_title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()

                # Description may be in content:encoded or description
                # content:encoded namespace
                desc = ""
                for child in item:
                    if "encoded" in child.tag:
                        desc = child.text or ""
                        break
                if not desc:
                    desc = (item.findtext("description") or "").strip()

                # Strip HTML from description
                plain_desc = re.sub(r"<[^>]+>", " ", desc)
                plain_desc = re.sub(r"\s+", " ", plain_desc).strip()

                # WWR titles are often "Company: Job Title"
                if ": " in raw_title:
                    company, title = raw_title.split(": ", 1)
                else:
                    company = None
                    title = raw_title

                if query_lower:
                    if query_lower not in title.lower() and query_lower not in plain_desc.lower():
                        continue

                jobs.append(
                    RawJob(
                        title=title[:300],
                        company=company[:200] if company else None,
                        location="Remote",
                        description=plain_desc[:5000],
                        source="weworkremotely",
                        url=link or None,
                    )
                )

        return jobs


class BuiltInScraper(JobScraper):
    """Scrape BuiltIn job listings via HTML parsing."""

    source_name = "builtin"
    _BASE_URL = "https://builtin.com"
    _LISTING_URL = "https://builtin.com/jobs/remote/dev-engineering"

    def scrape(self, query: str, location: str | None = None, limit: int = 25) -> list[RawJob]:
        import time

        from bs4 import BeautifulSoup

        # Cap to avoid hammering the site
        effective_limit = min(limit, 15)
        query_lower = query.lower() if query else ""

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        try:
            resp = httpx.get(self._LISTING_URL, headers=headers, timeout=20, follow_redirects=True)
            resp.raise_for_status()
        except Exception:
            logger.exception("Failed to fetch BuiltIn listing page")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        # BuiltIn uses data-id attributes on job cards; look for common card patterns
        cards = soup.select("[data-id]") or soup.select(".job-card") or soup.select("article")
        if not cards:
            # Fallback: look for links that point to /job/ paths
            cards = soup.select('a[href*="/job/"]')

        jobs: list[RawJob] = []

        for card in cards:
            if len(jobs) >= effective_limit:
                break

            # Extract title
            title_el = card.select_one("h2, h3, .job-title, [data-testid*='title']")
            title = title_el.get_text(strip=True) if title_el else card.get_text(strip=True)[:200]
            if not title:
                continue

            # Extract company
            company_el = card.select_one(".company-name, [data-testid*='company'], .employer")
            company = company_el.get_text(strip=True) if company_el else None

            # Extract location
            loc_el = card.select_one(".job-location, [data-testid*='location']")
            loc = loc_el.get_text(strip=True) if loc_el else "Remote"

            # Extract detail link
            link_el = card.select_one("a[href]") if card.name != "a" else card
            detail_url = None
            if link_el and link_el.get("href"):
                href = link_el["href"]
                detail_url = href if href.startswith("http") else f"{self._BASE_URL}{href}"

            # Fetch detail page for full description (with rate limiting)
            description = ""
            if detail_url:
                time.sleep(1)
                try:
                    detail_resp = httpx.get(
                        detail_url, headers=headers, timeout=15, follow_redirects=True
                    )
                    detail_resp.raise_for_status()
                    detail_soup = BeautifulSoup(detail_resp.text, "html.parser")
                    desc_el = detail_soup.select_one(
                        ".job-description, [data-testid*='description'], .description, article"
                    )
                    if desc_el:
                        description = re.sub(r"\s+", " ", desc_el.get_text(strip=True))[:5000]
                except Exception:
                    logger.debug("Failed to fetch BuiltIn detail page: %s", detail_url)

            if not description:
                description = title

            if query_lower:
                if query_lower not in title.lower() and query_lower not in description.lower():
                    continue

            jobs.append(
                RawJob(
                    title=title[:300],
                    company=company[:200] if company else None,
                    location=loc[:200],
                    description=description[:5000],
                    source="builtin",
                    url=detail_url,
                )
            )

        return jobs


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

SCRAPERS: dict[str, type[JobScraper]] = {
    "hn": HNHiringScraper,
    "indeed": IndeedScraper,
    "linkedin": LinkedInScraper,
    "remoteok": RemoteOKScraper,
    "weworkremotely": WeWorkRemotelyScraper,
    "builtin": BuiltInScraper,
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
