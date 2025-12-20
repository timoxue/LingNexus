from typing import List
from uuid import uuid4

from core_agents.intelligence_service.agents import analysis_agent, retrieval_agent
from core_agents.intelligence_service.schema import (
    DailyDigestItem,
    DailyDigestRequest,
    DailyDigestResponse,
    TopicConfig,
    UserConfig,
)
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


async def run_daily_digest(request: DailyDigestRequest) -> DailyDigestResponse:
    """订阅日报主流程。

    - 遍历请求中的每个 Topic；
    - 使用 RetrievalAgent 检索资讯；
    - 使用 AnalysisAgent 生成该主题的订阅日报；
    - 聚合为 DailyDigestResponse 返回。
    """

    topics: List[TopicConfig] = request.topics or []
    users: List[UserConfig] = request.users or []

    if not topics:
        task_id = f"daily_{uuid4()}"
        logger.warning("Daily digest called with empty topics list")
        return DailyDigestResponse(task_id=task_id, status="empty", items=[])

    items: List[DailyDigestItem] = []

    for topic in topics:
        logger.info(
            "DailyDigest processing topic",
            extra={"topic_id": topic.topic_id, "topic_name": topic.name},
        )

        # 1. 检索资讯
        news_list = await retrieval_agent.fetch_news_for_topic(topic)

        # 2. 构建订阅日报
        digest_item = await analysis_agent.build_digest(topic, news_list, users=users)
        items.append(digest_item)

    task_id = f"daily_{uuid4()}"
    logger.info(
        "DailyDigest completed",
        extra={"task_id": task_id, "topic_count": len(items)},
    )

    return DailyDigestResponse(task_id=task_id, status="completed", items=items)
