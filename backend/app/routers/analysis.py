from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.analyzer import (
    get_analysis_summary,
    get_gap_analysis,
    get_niche_analysis,
    get_profile_suggestions,
    get_skill_trends,
    get_skill_values,
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


# ---- Niche Analysis -----------------------------------------------------------


class NicheSkillResponse(BaseModel):
    name: str
    category: str
    count: int
    percentage: float


class NicheAnalysisResponse(BaseModel):
    niche_name: str
    total_jobs_in_niche: int
    total_jobs_overall: int
    niche_percentage: float
    core_skills: list[NicheSkillResponse]
    differentiator_skills: list[NicheSkillResponse]
    complementary_skills: list[str]
    career_paths: list[str]


@router.get("/niche", response_model=NicheAnalysisResponse)
def niche_analysis(
    skills: str = Query(..., description="Comma-separated list of niche skills"),
    name: str = Query("Custom", description="Human-readable niche name"),
    db: Session = Depends(get_db),
):
    """Analyze a skill niche -- find jobs that require these skills and what else they need."""
    skill_list = [s.strip() for s in skills.split(",") if s.strip()]
    if not skill_list:
        raise HTTPException(400, "At least one skill is required")

    result = get_niche_analysis(db, niche_skills=skill_list, niche_name=name)
    return NicheAnalysisResponse(
        niche_name=result.niche_name,
        total_jobs_in_niche=result.total_jobs_in_niche,
        total_jobs_overall=result.total_jobs_overall,
        niche_percentage=result.niche_percentage,
        core_skills=[
            NicheSkillResponse(name=s.name, category=s.category, count=s.count, percentage=s.percentage)
            for s in result.core_skills
        ],
        differentiator_skills=[
            NicheSkillResponse(name=s.name, category=s.category, count=s.count, percentage=s.percentage)
            for s in result.differentiator_skills
        ],
        complementary_skills=result.complementary_skills,
        career_paths=result.career_paths,
    )


# ---- Skill Value Analysis ----------------------------------------------------


class SkillValueResponse(BaseModel):
    name: str
    category: str
    job_count: int
    avg_salary: float
    median_salary: float
    salary_premium: float
    value_score: float


class SkillValueReportResponse(BaseModel):
    overall_avg_salary: float
    overall_median_salary: float
    total_jobs_with_salary: int
    skills: list[SkillValueResponse]


@router.get("/skill-values", response_model=SkillValueReportResponse)
def skill_values(
    min_jobs: int = Query(2, ge=1, description="Minimum jobs mentioning a skill to include it"),
    limit: int = Query(30, ge=1, le=200, description="Max skills to return"),
    db: Session = Depends(get_db),
):
    """Calculate the dollar value of each skill based on salary data in job postings."""
    report = get_skill_values(db, min_jobs=min_jobs, limit=limit)
    return SkillValueReportResponse(
        overall_avg_salary=report.overall_avg_salary,
        overall_median_salary=report.overall_median_salary,
        total_jobs_with_salary=report.total_jobs_with_salary,
        skills=[
            SkillValueResponse(
                name=sv.name,
                category=sv.category,
                job_count=sv.job_count,
                avg_salary=sv.avg_salary,
                median_salary=sv.median_salary,
                salary_premium=sv.salary_premium,
                value_score=sv.value_score,
            )
            for sv in report.skills
        ],
    )


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
