from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.analyzer import (
    get_analysis_summary,
    get_gap_analysis,
    get_profile_suggestions,
    get_skill_trends,
)

router = APIRouter()


class GapAnalysisResponse(BaseModel):
    match_percentage: float
    matching_skills: list[str]
    missing_skills: list[dict]
    undervalued_skills: list[str]
    high_value_skills: list[str]
    top_recommendations: list[str]


class ProfileSuggestionResponse(BaseModel):
    headline_options: list[str]
    missing_keywords: list[str]
    trending_skills: list[str]


@router.get("/gap/{profile_id}", response_model=GapAnalysisResponse)
def gap_analysis(profile_id: int, db: Session = Depends(get_db)):
    """Compare your skills against market demand."""
    result = get_gap_analysis(db, profile_id)
    if not result:
        raise HTTPException(404, "Profile not found")
    return GapAnalysisResponse(
        match_percentage=result.match_percentage,
        matching_skills=result.matching_skills,
        missing_skills=[
            {"name": s.name, "category": s.category, "count": s.count, "percentage": s.percentage}
            for s in result.missing_skills
        ],
        undervalued_skills=result.undervalued_skills,
        high_value_skills=result.high_value_skills,
        top_recommendations=result.top_recommendations,
    )


@router.get("/profile-suggestions/{profile_id}", response_model=ProfileSuggestionResponse)
def profile_suggestions(profile_id: int, db: Session = Depends(get_db)):
    """Get LinkedIn profile optimization suggestions."""
    result = get_profile_suggestions(db, profile_id)
    if not result:
        raise HTTPException(404, "Profile not found")
    return ProfileSuggestionResponse(
        headline_options=result.headline_options,
        missing_keywords=result.missing_keywords,
        trending_skills=result.trending_skills,
    )


# ---- Trends & Summary -------------------------------------------------------


class TrendPeriodResponse(BaseModel):
    date: str
    count: int


class SkillTrendResponse(BaseModel):
    skill_name: str
    periods: list[TrendPeriodResponse]


class SummaryResponse(BaseModel):
    total_jobs: int
    total_skills: int
    top_category: str | None
    avg_skills_per_job: float


@router.get("/trends", response_model=list[SkillTrendResponse])
def trends(
    period: str = Query("weekly", pattern="^(weekly|monthly)$"),
    top_n: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Skill demand over time, grouped by week or month."""
    results = get_skill_trends(db, period=period, top_n=top_n)
    return [
        SkillTrendResponse(
            skill_name=t.skill_name,
            periods=[TrendPeriodResponse(date=p.date, count=p.count) for p in t.periods],
        )
        for t in results
    ]


@router.get("/summary", response_model=SummaryResponse)
def summary(db: Session = Depends(get_db)):
    """Overall dataset statistics."""
    s = get_analysis_summary(db)
    return SummaryResponse(
        total_jobs=s.total_jobs,
        total_skills=s.total_skills,
        top_category=s.top_category,
        avg_skills_per_job=s.avg_skills_per_job,
    )
