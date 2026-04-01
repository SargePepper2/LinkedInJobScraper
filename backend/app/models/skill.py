import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class SkillCategory(str, enum.Enum):
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    DATABASE = "database"
    CLOUD = "cloud"
    TOOL = "tool"
    METHODOLOGY = "methodology"
    SOFT_SKILL = "soft_skill"
    OTHER = "other"


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    category: Mapped[SkillCategory] = mapped_column(Enum(SkillCategory))
    aliases: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    is_primary: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    occurrences: Mapped[list["SkillOccurrence"]] = relationship(back_populates="skill")  # noqa: F821
