"""RD compound analysis skill.

Analyze compound properties for drug R&D scenarios.
"""

from typing import Optional

from shared.models.llm_manager import llm_manager
from shared.prompts.manager import prompt_manager
from shared.skills.base_skill import BaseSkill, SkillInput, SkillOutput
from shared.skills.registry import register_skill
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


class RDCompoundAnalysisInput(SkillInput):
    """输入：化合物分析所需信息。"""

    compound: str
    context: Optional[str] = None


@register_skill
class RDCompoundAnalysisSkill(BaseSkill):
    """化合物分析技能。

    基于化合物信息与背景资料，生成结构化的研发分析报告。
    """

    name: str = "rd.compound_analysis"
    description: str = "分析化合物特性与成药性"
    domain: str = "rd"
    category: str = "analysis"
    tags = ["rd", "compound", "analysis"]

    async def execute(self, input_data: RDCompoundAnalysisInput) -> SkillOutput:
        prompt_key = "rd_compound_analysis_v1"

        prompt_text = prompt_manager.render(
            service="rd",
            key=prompt_key,
            compound=input_data.compound,
            context=input_data.context or "无额外背景信息",
        )

        model_name = prompt_manager.get_recommended_model("rd", prompt_key)

        logger.info(
            "RDCompoundAnalysisSkill executing",
            extra={"compound": input_data.compound, "model": model_name},
        )

        messages = [
            {"role": "system", "content": prompt_text},
        ]

        summary = await llm_manager.chat(messages, model_name=model_name)

        return SkillOutput(
            success=True,
            data=summary,
            message="化合物分析完成",
            meta={"compound": input_data.compound},
        )
