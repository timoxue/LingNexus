"""Registry for managing skills.

Provides utilities to register and retrieve skills by name, as well as list them
by domain or category.
"""

from typing import Dict, List, Optional, Type

from shared.skills.base_skill import BaseSkill
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

_SKILLS: Dict[str, BaseSkill] = {}


def register_skill(cls: Type[BaseSkill]) -> Type[BaseSkill]:
    """Class decorator to register a skill.

    It instantiates the skill class once and stores the instance in a global registry
    keyed by its `name` attribute.
    """

    try:
        instance = cls()
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Failed to instantiate skill", extra={"class": cls.__name__, "error": str(exc)})
        raise

    name = getattr(instance, "name", cls.__name__)
    if name in _SKILLS:
        logger.warning("Skill name already registered, overriding", extra={"name": name})

    _SKILLS[name] = instance
    logger.info("Skill registered", extra={"name": name, "domain": getattr(instance, "domain", None), "category": getattr(instance, "category", None)})
    return cls


def get_skill(name: str) -> Optional[BaseSkill]:
    """Retrieve a registered skill instance by name."""

    return _SKILLS.get(name)


def list_skills(domain: Optional[str] = None, category: Optional[str] = None) -> List[BaseSkill]:
    """List all registered skills, optionally filtered by domain and category."""

    skills = list(_SKILLS.values())
    if domain is not None:
        skills = [s for s in skills if getattr(s, "domain", None) == domain]
    if category is not None:
        skills = [s for s in skills if getattr(s, "category", None) == category]
    return skills


__all__ = ["register_skill", "get_skill", "list_skills"]
