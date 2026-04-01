from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    target_role: Mapped[str | None] = mapped_column(String(300))
    headline: Mapped[str | None] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    skills: Mapped[list["UserSkill"]] = relationship(back_populates="profile")


class UserSkill(Base):
    __tablename__ = "user_skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_profile_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE")
    )
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"))
    proficiency_level: Mapped[int] = mapped_column(Integer, default=3)  # 1-5 scale

    profile: Mapped[UserProfile] = relationship(back_populates="skills")
    skill: Mapped["Skill"] = relationship()  # noqa: F821
