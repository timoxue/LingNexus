"""Intelligence retrieval related skills.

These skills encapsulate how to fetch raw news items for a given topic.
"""

from typing import Any, Dict, List

from shared.skills.base_skill import BaseSkill, SkillInput, SkillOutput
from shared.skills.registry import register_skill
from shared.storage import es_client
from shared.storage.es_query_medical import query_news_by_topic
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


class FetchNewsInput(SkillInput):
    """资讯检索技能的输入模型。"""

    topic_name: str
    keywords: List[str]
    max_items: int


@register_skill
class FetchNewsSkill(BaseSkill):
    """根据主题检索原始资讯列表的技能实现。"""

    name: str = "intel.fetch_news"
    description: str = "根据主题与关键词检索医药资讯"
    domain: str = "intelligence"
    category: str = "retrieval"
    tags = ["news", "pharma", "subscription"]

    async def execute(self, input_data: FetchNewsInput) -> SkillOutput:
        raw_items = await fetch_raw_news_for_topic(
            topic_name=input_data.topic_name,
            keywords=input_data.keywords,
            max_items=input_data.max_items,
        )

        return SkillOutput(
            success=True,
            data=raw_items,
            message="资讯检索成功",
            meta={"topic": input_data.topic_name, "count": len(raw_items)},
        )


async def fetch_raw_news_for_topic(
    topic_name: str,
    keywords: List[str],
    max_items: int,
) -> List[Dict[str, Any]]:
    """根据主题名称和关键词检索原始资讯列表的函数封装。

    返回的结果是原始 dict 列表，字段结构与 `pharma_news` 索引一致，
    由上层 Agent 或服务负责转换为各自的业务模型（如 NewsItem）。
    """

    logger.info(
        "FetchNewsSkill fetching news",
        extra={"topic": topic_name, "keywords": keywords, "max_items": max_items},
    )

    raw_items = await query_news_by_topic(
        es_client=es_client,
        topic=topic_name,
        keywords=keywords,
        top_k=max_items,
    )

    logger.info(
        "FetchNewsSkill fetched news successfully",
        extra={"topic": topic_name, "count": len(raw_items)},
    )

    return raw_items
