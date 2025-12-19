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
