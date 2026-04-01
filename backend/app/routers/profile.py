from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.skill import Skill
from app.models.user_profile import UserProfile, UserSkill

router = APIRouter()


class CreateProfileRequest(BaseModel):
    name: str
    target_role: str | None = None
    headline: str | None = None
    summary: str | None = None
    skill_names: list[str] = []


class ProfileResponse(BaseModel):
    id: int
    name: str
    target_role: str | None
    headline: str | None
    skills: list[str]

    model_config = {"from_attributes": True}


@router.post("/", response_model=ProfileResponse)
def create_profile(req: CreateProfileRequest, db: Session = Depends(get_db)):
    """Create a user profile with current skills."""
    profile = UserProfile(
        name=req.name,
        target_role=req.target_role,
        headline=req.headline,
        summary=req.summary,
    )
    db.add(profile)
    db.flush()

    skill_names = []
    for name in req.skill_names:
        skill = db.query(Skill).filter(Skill.name.ilike(name)).first()
        if skill:
            us = UserSkill(user_profile_id=profile.id, skill_id=skill.id)
            db.add(us)
            skill_names.append(skill.name)

    db.commit()
    return ProfileResponse(
        id=profile.id,
        name=profile.name,
        target_role=profile.target_role,
        headline=profile.headline,
        skills=skill_names,
    )


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """Get a user profile."""
    profile = db.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    skill_names = []
    for us in profile.skills:
        skill = db.get(Skill, us.skill_id)
        if skill:
            skill_names.append(skill.name)
    return ProfileResponse(
        id=profile.id,
        name=profile.name,
        target_role=profile.target_role,
        headline=profile.headline,
        skills=skill_names,
    )


class AddSkillsRequest(BaseModel):
    skill_names: list[str]


@router.post("/{profile_id}/skills")
def add_skills(profile_id: int, req: AddSkillsRequest, db: Session = Depends(get_db)):
    """Add skills to a profile."""
    profile = db.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")

    added = []
    for name in req.skill_names:
        skill = db.query(Skill).filter(Skill.name.ilike(name)).first()
        if skill:
            existing = (
                db.query(UserSkill)
                .filter(UserSkill.user_profile_id == profile_id, UserSkill.skill_id == skill.id)
                .first()
            )
            if not existing:
                db.add(UserSkill(user_profile_id=profile_id, skill_id=skill.id))
                added.append(skill.name)

    db.commit()
    return {"added": added}
