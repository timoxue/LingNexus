from typing import Optional

from shared.models.llm_manager import llm_manager
from shared.prompts.manager import prompt_manager
from shared.skills.base_skill import BaseSkill, SkillInput, SkillOutput
from shared.skills.registry import register_skill
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


class DailyDigestInput(SkillInput):
    """订阅日报生成技能的输入模型。"""

    topic_name: str
    topic_description: str = ""
    news_items_text: str
    role: Optional[str] = None


@register_skill
class GenerateDailyDigestSkill(BaseSkill):
    """为指定主题生成订阅日报摘要的技能实现。"""

    name: str = "intel.generate_daily_digest"
    description: str = "根据候选资讯生成订阅日报文本"
    domain: str = "intelligence"
    category: str = "reporting"
    tags = ["subscription", "digest", "pharma", "news"]

    async def execute(self, input_data: DailyDigestInput) -> SkillOutput:
        digest_summary = await generate_daily_digest_text(
            topic_name=input_data.topic_name,
            topic_description=input_data.topic_description,
            news_items_text=input_data.news_items_text,
            role=input_data.role,
        )

        return SkillOutput(
            success=True,
            data=digest_summary,
            message="订阅日报生成成功",
            meta={"topic": input_data.topic_name, "role": input_data.role or "综合读者"},
        )


async def generate_daily_digest_text(
    topic_name: str,
    topic_description: str,
    news_items_text: str,
    role: Optional[str] = None,
) -> str:
    """订阅日报生成技能的函数封装。

    给定订阅主题、说明、候选资讯文本和角色信息，生成一篇可直接推送的订阅日报文本。

    该函数保留原有调用方式，便于已有 Agent / Workflow 复用，内部逻辑与
    GenerateDailyDigestSkill 保持一致。
    """

    prompt_key = "intelligence_daily_digest_v1"

    prompt_text = prompt_manager.render(
        service="intelligence",
        key=prompt_key,
        topic_name=topic_name,
        topic_description=topic_description,
        news_items=news_items_text,
        target_role=role or "综合读者",
    )

    recommended_model = prompt_manager.get_recommended_model("intelligence", prompt_key)

    logger.info(
        "DailyDigestSkill generating digest",
        extra={
            "topic": topic_name,
            "role": role or "综合读者",
            "model": recommended_model,
        },
    )

    messages = [
        {"role": "system", "content": prompt_text},
        {"role": "user", "content": "请根据上述要求生成适合推送的订阅日报。"},
    ]

    digest_summary = await llm_manager.chat(messages, model_name=recommended_model)

    return digest_summary
