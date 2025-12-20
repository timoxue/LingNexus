"""BD lead qualification skill.

Evaluate potential BD opportunities using LLM and prompt templates.
"""

from typing import Optional

from shared.models.llm_manager import llm_manager
from shared.prompts.manager import prompt_manager
from shared.skills.base_skill import BaseSkill, SkillInput, SkillOutput
from shared.skills.registry import register_skill
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


class BDLeadQualificationInput(SkillInput):
    """输入：BD 线索评估所需信息。"""

    target: str
    context: Optional[str] = None


@register_skill
class BDLeadQualificationSkill(BaseSkill):
    """BD 线索评估技能。

    基于目标企业/项目与上下文信息，生成结构化的 BD 评估结果。
    """

    name: str = "bd.lead_qualification"
    description: str = "评估潜在 BD 合作机会的优先级与关键要点"
    domain: str = "bd"
    category: str = "analysis"
    tags = ["bd", "lead", "evaluation"]

    async def execute(self, input_data: BDLeadQualificationInput) -> SkillOutput:
        prompt_key = "bd_lead_qualification_v1"

        prompt_text = prompt_manager.render(
            service="bd",
            key=prompt_key,
            target=input_data.target,
            context=input_data.context or "无额外背景信息",
        )

        model_name = prompt_manager.get_recommended_model("bd", prompt_key)

        logger.info(
            "BDLeadQualificationSkill executing",
            extra={"target": input_data.target, "model": model_name},
        )

        messages = [
            {"role": "system", "content": prompt_text},
        ]

        summary = await llm_manager.chat(messages, model_name=model_name)

        return SkillOutput(
            success=True,
            data=summary,
            message="BD 线索评估完成",
            meta={"target": input_data.target},
        )
