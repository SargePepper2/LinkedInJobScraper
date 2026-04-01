from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50))
    query: Mapped[str | None] = mapped_column(String(500))
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    jobs_found: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="running")

    jobs: Mapped[list["Job"]] = relationship(back_populates="scrape_run")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    company: Mapped[str | None] = mapped_column(String(200))
    location: Mapped[str | None] = mapped_column(String(200))
    salary_min: Mapped[int | None] = mapped_column(Integer)
    salary_max: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(50), default="manual")
    source_url: Mapped[str | None] = mapped_column(String(1000))
    fingerprint: Mapped[str | None] = mapped_column(String(64), index=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    scrape_run_id: Mapped[int | None] = mapped_column(ForeignKey("scrape_runs.id"))

    scrape_run: Mapped[ScrapeRun | None] = relationship(back_populates="jobs")
    skill_occurrences: Mapped[list["SkillOccurrence"]] = relationship(back_populates="job")


class SkillOccurrence(Base):
    __tablename__ = "skill_occurrences"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"))
    context_snippet: Mapped[str | None] = mapped_column(String(500))

    job: Mapped[Job] = relationship(back_populates="skill_occurrences")
    skill: Mapped["Skill"] = relationship(back_populates="occurrences")  # noqa: F821
