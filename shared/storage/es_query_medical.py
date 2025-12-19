from typing import Any, Dict, List

from shared.storage.es_client import ESClient
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


async def search_clinical_trials(
    es_client: ESClient, query: str, filters: Dict[str, Any], top_k: int = 10
) -> List[Dict[str, Any]]:
    """搜索临床试验（骨架）。"""
    logger.info("Searching clinical trials", extra={"query": query})
    # TODO: 实现真实 ES 查询
    return []


async def search_patents(
    es_client: ESClient, query: str, filters: Dict[str, Any], top_k: int = 10
) -> List[Dict[str, Any]]:
    """搜索专利（骨架）。"""
    logger.info("Searching patents", extra={"query": query})
    # TODO: 实现真实 ES 查询
    return []


async def search_research_reports(
    es_client: ESClient, query: str, filters: Dict[str, Any], top_k: int = 10
) -> List[Dict[str, Any]]:
    """搜索研报（骨架）。"""
    logger.info("Searching research reports", extra={"query": query})
    # TODO: 实现真实 ES 查询
    return []


async def query_news_by_topic(
    es_client: ESClient,
    topic: str,
    keywords: List[str] | None = None,
    top_k: int = 20,
) -> List[Dict[str, Any]]:
    """按照主题检索医药资讯（基于 local_file ES 的简易实现）。

    - topic: 主题名称（如 "PD-1 肺癌"）
    - keywords: 可选关键词列表；如为空，则默认使用 topic 作为搜索词
    - top_k: 返回的最大数量
    """
    # 组合关键词（local_file 模式下，底层是简单全文匹配）
    if keywords:
        query_text = " ".join(keywords)
    else:
        query_text = topic

    logger.info(
        "Searching pharma news by topic",
        extra={"topic": topic, "keywords": keywords, "top_k": top_k},
    )

    es_query = {
        "query": {
            "query_string": {
                "query": query_text,
            }
        }
    }

    resp = await es_client.search(index="pharma_news", query=es_query)
    hits = resp.get("hits", [])

    # local_file 模式下，search 已经直接返回文档列表
    if isinstance(hits, list):
        return hits[:top_k]

    # 兼容未来接入真实 ES 的结构
    return [h.get("_source", {}) for h in hits][:top_k]
