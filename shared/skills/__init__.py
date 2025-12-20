"""Shared skill library entry point.

This module exposes reusable skills and common abstractions that
can be used across services.
"""

from shared.skills.base_skill import BaseSkill, SkillInput, SkillOutput
from shared.skills.registry import get_skill, list_skills, register_skill

__all__ = [
    "BaseSkill",
    "SkillInput",
    "SkillOutput",
    "get_skill",
    "list_skills",
    "register_skill",
]
