"""Core abstractions for skills used across services.

Defines the base classes for skill input/output and the abstract BaseSkill.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class SkillInput(BaseModel):
    """Base class for all skill input models.

    Concrete skills should define their own input models inheriting from this.
    """


class SkillOutput(BaseModel):
    """Standard output model for all skills."""

    success: bool = True
    data: Any = None
    message: str = ""
    meta: Dict[str, Any] = Field(default_factory=dict)


class BaseSkill(ABC):
    """Abstract base class for all skills.

    A skill represents a reusable capability that can be invoked by agents or workflows.
    """

    # Basic metadata
    name: str = "base_skill"
    description: str = "Base skill"
    domain: str = "generic"  # e.g. "intelligence", "bd", "rd"
    category: str = "generic"  # e.g. "retrieval", "analysis", "reporting"
    version: str = "v1"
    tags: List[str] = []

    @abstractmethod
    async def execute(self, input_data: SkillInput) -> SkillOutput:
        """Execute the skill with the given input and return a SkillOutput.

        Concrete skills must implement this method.
        """

        raise NotImplementedError
