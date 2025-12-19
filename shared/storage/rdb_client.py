from typing import Optional

from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


class RDBClient:
    """关系型数据库客户端骨架（支持 MySQL/PostgreSQL）。

    后续可以使用 SQLAlchemy 或其他 ORM。
    """

    def __init__(self, url: str) -> None:
        self.url = url
        logger.info("RDB client initialized", extra={"url": url})

    async def execute(self, query: str) -> Optional[list]:
        """执行 SQL（骨架）。"""
        logger.info("RDB execute called", extra={"query": query})
        # TODO: 实现真实数据库连接与查询
        return None
