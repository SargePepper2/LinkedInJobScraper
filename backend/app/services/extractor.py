"""Skill extraction engine — multi-pass taxonomy-based matching."""

import json
import re
from dataclasses import dataclass
from pathlib import Path

_TAXONOMY_PATH = Path(__file__).parent.parent.parent / "data" / "skill_taxonomy.json"


@dataclass
class ExtractedSkill:
    name: str
    category: str
    context: str  # surrounding text snippet
    match_type: str  # exact, alias, regex, context


class SkillExtractor:
    def __init__(self, taxonomy_path: Path = _TAXONOMY_PATH):
        with open(taxonomy_path) as f:
            self._taxonomy = json.load(f)
        self._build_lookup()

    def _build_lookup(self) -> None:
        """Build fast lookup maps from taxonomy."""
        # name -> skill entry
        self._by_name: dict[str, dict] = {}
        # alias (lowered) -> canonical name
        self._alias_map: dict[str, str] = {}
        # compiled regex patterns for tricky names (C++, .NET, Node.js, etc.)
        self._regex_patterns: list[tuple[re.Pattern, str, str]] = []

        for skill in self._taxonomy:
            name = skill["name"]
            category = skill["category"]
            self._by_name[name.lower()] = skill

            for alias in skill.get("aliases", []):
                self._alias_map[alias.lower()] = name

            # Build regex for names with special chars
            if any(c in name for c in ".+#/"):
                pattern = re.compile(
                    r"\b" + re.escape(name) + r"\b",
                    re.IGNORECASE,
                )
                self._regex_patterns.append((pattern, name, category))

    def extract(self, text: str) -> list[ExtractedSkill]:
        """Extract skills from a job description using multi-pass matching."""
        results: dict[str, ExtractedSkill] = {}
        text_lower = text.lower()

        # Pass 1: Exact match on skill names
        for name_lower, skill in self._by_name.items():
            if self._word_match(name_lower, text_lower):
                ctx = self._get_context(name_lower, text_lower, text)
                results[skill["name"]] = ExtractedSkill(
                    name=skill["name"],
                    category=skill["category"],
                    context=ctx,
                    match_type="exact",
                )

        # Pass 2: Alias resolution
        for alias_lower, canonical in self._alias_map.items():
            if canonical in results:
                continue
            if self._word_match(alias_lower, text_lower):
                skill = self._by_name[canonical.lower()]
                ctx = self._get_context(alias_lower, text_lower, text)
                results[canonical] = ExtractedSkill(
                    name=canonical,
                    category=skill["category"],
                    context=ctx,
                    match_type="alias",
                )

        # Pass 3: Regex for special-character names (C++, .NET, Node.js)
        for pattern, name, category in self._regex_patterns:
            if name in results:
                continue
            match = pattern.search(text)
            if match:
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                ctx = text[start:end].strip()
                results[name] = ExtractedSkill(
                    name=name,
                    category=category,
                    context=ctx,
                    match_type="regex",
                )

        # Pass 4: Context detection — "X+ years of {skill}" patterns
        experience_pattern = re.compile(
            r"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience\s+(?:with|in|using)\s+)?(\w[\w\s.#+/]*)",
            re.IGNORECASE,
        )
        for match in experience_pattern.finditer(text):
            skill_text = match.group(2).strip().lower()
            # Check if it matches a known skill
            if skill_text in self._by_name and skill_text not in {
                r.name.lower() for r in results.values()
            }:
                skill = self._by_name[skill_text]
                results[skill["name"]] = ExtractedSkill(
                    name=skill["name"],
                    category=skill["category"],
                    context=match.group(0),
                    match_type="context",
                )

        return list(results.values())

    def _word_match(self, term: str, text: str) -> bool:
        """Check if term appears as a whole word in text."""
        pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        return bool(pattern.search(text))

    def _get_context(self, term: str, text_lower: str, original: str) -> str:
        """Get surrounding context snippet for a match."""
        idx = text_lower.find(term)
        if idx == -1:
            return ""
        start = max(0, idx - 40)
        end = min(len(original), idx + len(term) + 40)
        return original[start:end].strip()
