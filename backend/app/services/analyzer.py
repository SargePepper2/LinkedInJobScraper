"""Skill analysis — rankings, co-occurrence, gap analysis, profile optimization."""

from collections import Counter
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.job import Job, SkillOccurrence
from app.models.skill import Skill
from app.models.user_profile import UserProfile, UserSkill


@dataclass
class SkillRanking:
    name: str
    category: str
    count: int
    percentage: float  # % of jobs mentioning this skill


@dataclass
class CoOccurrence:
    skill_a: str
    skill_b: str
    count: int


@dataclass
class GapAnalysis:
    match_percentage: float
    matching_skills: list[str]
    missing_skills: list[SkillRanking]  # skills in demand that user lacks
    undervalued_skills: list[str]  # user has but rarely demanded
    high_value_skills: list[str]  # user has AND highly demanded
    top_recommendations: list[str]  # ordered list of what to learn next


@dataclass
class ProfileSuggestion:
    headline_options: list[str]
    missing_keywords: list[str]  # skills you have but aren't listing
    trending_skills: list[str]  # your skills that are trending up


def get_skill_rankings(db: Session, limit: int = 50) -> list[SkillRanking]:
    """Get skills ranked by occurrence count across all jobs."""
    total_jobs = db.scalar(select(func.count(Job.id))) or 1

    rows = (
        db.execute(
            select(Skill.name, Skill.category, func.count(SkillOccurrence.id).label("cnt"))
            .join(SkillOccurrence, SkillOccurrence.skill_id == Skill.id)
            .group_by(Skill.name, Skill.category)
            .order_by(func.count(SkillOccurrence.id).desc())
            .limit(limit)
        )
        .all()
    )

    return [
        SkillRanking(
            name=name,
            category=category.value if hasattr(category, "value") else category,
            count=cnt,
            percentage=round(cnt / total_jobs * 100, 1),
        )
        for name, category, cnt in rows
    ]


def get_co_occurrences(db: Session, min_count: int = 3, limit: int = 50) -> list[CoOccurrence]:
    """Find skills that frequently appear together in the same job."""
    so1 = SkillOccurrence.__table__.alias("so1")
    so2 = SkillOccurrence.__table__.alias("so2")
    s1 = Skill.__table__.alias("s1")
    s2 = Skill.__table__.alias("s2")

    rows = (
        db.execute(
            select(
                s1.c.name.label("a"),
                s2.c.name.label("b"),
                func.count().label("cnt"),
            )
            .select_from(so1)
            .join(so2, (so1.c.job_id == so2.c.job_id) & (so1.c.skill_id < so2.c.skill_id))
            .join(s1, so1.c.skill_id == s1.c.id)
            .join(s2, so2.c.skill_id == s2.c.id)
            .group_by(s1.c.name, s2.c.name)
            .having(func.count() >= min_count)
            .order_by(func.count().desc())
            .limit(limit)
        )
        .all()
    )

    return [CoOccurrence(skill_a=a, skill_b=b, count=cnt) for a, b, cnt in rows]


def get_gap_analysis(db: Session, profile_id: int) -> GapAnalysis | None:
    """Compare user's skills against market demand."""
    profile = db.get(UserProfile, profile_id)
    if not profile:
        return None

    # Get user's current skills
    user_skill_ids = {us.skill_id for us in profile.skills}
    user_skill_names = set()
    for us in profile.skills:
        skill = db.get(Skill, us.skill_id)
        if skill:
            user_skill_names.add(skill.name)

    # Get market rankings
    rankings = get_skill_rankings(db, limit=100)
    ranking_names = {r.name for r in rankings}

    matching = user_skill_names & ranking_names
    missing = [r for r in rankings if r.name not in user_skill_names]
    undervalued = [name for name in user_skill_names if name not in ranking_names]
    high_value = [r.name for r in rankings[:20] if r.name in user_skill_names]

    match_pct = round(len(matching) / max(len(rankings[:20]), 1) * 100, 1)
    top_recs = [r.name for r in missing[:10]]

    return GapAnalysis(
        match_percentage=match_pct,
        matching_skills=sorted(matching),
        missing_skills=missing[:20],
        undervalued_skills=undervalued,
        high_value_skills=high_value,
        top_recommendations=top_recs,
    )


def get_profile_suggestions(
    db: Session, profile_id: int
) -> ProfileSuggestion | None:
    """Generate LinkedIn profile optimization suggestions."""
    profile = db.get(UserProfile, profile_id)
    if not profile:
        return None

    rankings = get_skill_rankings(db, limit=30)
    top_skill_names = {r.name for r in rankings}

    # User's skill names
    user_skill_names = set()
    for us in profile.skills:
        skill = db.get(Skill, us.skill_id)
        if skill:
            user_skill_names.add(skill.name)

    # Skills user has that are in-demand — good for headline
    headline_skills = [r.name for r in rankings if r.name in user_skill_names][:5]

    # Generate headline options
    role = profile.target_role or "Software Engineer"
    headlines = []
    if headline_skills:
        headlines.append(f"{role} | {' | '.join(headline_skills[:3])}")
        headlines.append(f"{role} specializing in {', '.join(headline_skills[:3])}")
        headlines.append(
            f"{headline_skills[0]} & {headline_skills[1]} {role}"
            if len(headline_skills) >= 2
            else f"{headline_skills[0]} {role}"
        )

    # Skills user has but may not be listing on profile
    mentioned_in_summary = set()
    if profile.summary:
        summary_lower = profile.summary.lower()
        for name in user_skill_names:
            if name.lower() in summary_lower:
                mentioned_in_summary.add(name)
    missing_keywords = sorted(user_skill_names - mentioned_in_summary)

    # Trending = in demand AND user has them
    trending = [r.name for r in rankings[:15] if r.name in user_skill_names]

    return ProfileSuggestion(
        headline_options=headlines,
        missing_keywords=missing_keywords,
        trending_skills=trending,
    )
