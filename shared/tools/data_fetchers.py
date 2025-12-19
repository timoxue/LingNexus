from typing import Any, Dict, Optional

import httpx

from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


async def fetch_http_data(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """通用 HTTP 数据抓取工具（骨架）。"""
    logger.info("Fetching HTTP data", extra={"url": url})
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
