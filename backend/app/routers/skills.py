from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.analyzer import (
    CoOccurrence,
    SkillRanking,
    get_co_occurrences,
    get_skill_rankings,
)

router = APIRouter()


class SkillRankingResponse(BaseModel):
    name: str
    category: str
    count: int
    percentage: float


class CoOccurrenceResponse(BaseModel):
    skill_a: str
    skill_b: str
    count: int


@router.get("/rankings", response_model=list[SkillRankingResponse])
def skill_rankings(limit: int = 50, db: Session = Depends(get_db)):
    """Get skills ranked by demand (occurrence count)."""
    rankings = get_skill_rankings(db, limit)
    return [
        SkillRankingResponse(
            name=r.name, category=r.category, count=r.count, percentage=r.percentage
        )
        for r in rankings
    ]


@router.get("/co-occurrence", response_model=list[CoOccurrenceResponse])
def co_occurrence(min_count: int = 3, limit: int = 50, db: Session = Depends(get_db)):
    """Get skill pairs that frequently appear together."""
    pairs = get_co_occurrences(db, min_count, limit)
    return [CoOccurrenceResponse(skill_a=p.skill_a, skill_b=p.skill_b, count=p.count) for p in pairs]
