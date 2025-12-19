from typing import List

from core_agents.intelligence_service.schema import NewsItem, TopicConfig
from shared.storage import es_client
from shared.storage.es_query_medical import query_news_by_topic
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


class RetrievalAgent:
    """负责根据主题从 ES/本地数据中检索相关资讯的智能体。"""

    async def fetch_news_for_topic(self, topic: TopicConfig) -> List[NewsItem]:
        """针对单个订阅主题检索医药资讯。

        当前实现基于 local_file ES（pharma_news.json），后续可平滑切换到真实 ES。
        """
        # 优先使用配置中的关键词，其次使用主题名称
        keywords = topic.keywords or [topic.name]

        logger.info(
            "RetrievalAgent fetching news",
            extra={"topic": topic.name, "keywords": keywords, "max_items": topic.max_items},
        )

        raw_items = await query_news_by_topic(
            es_client=es_client,
            topic=topic.name,
            keywords=keywords,
            top_k=topic.max_items,
        )

        news_list: List[NewsItem] = []
        for item in raw_items:
            # 将 dict 转换为 NewsItem 模型，字段缺失时使用默认值
            news = NewsItem(
                id=str(item.get("id", "")),
                title=item.get("title", ""),
                summary=item.get("summary"),
                source=item.get("source"),
                category=item.get("category"),
                tags=item.get("tags", []) or [],
                published_at=item.get("published_at"),
                url=item.get("url"),
                score=item.get("score"),
            )
            news_list.append(news)

        logger.info(
            "RetrievalAgent fetched news successfully",
            extra={"topic": topic.name, "count": len(news_list)},
        )
        return news_list


retrieval_agent = RetrievalAgent()
