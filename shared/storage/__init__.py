"""存储层统一初始化。"""
from config.settings import settings
from shared.storage.es_client import ESClient
from shared.storage.rdb_client import RDBClient

# 根据配置初始化 ES 客户端
es_client = ESClient(
    backend=settings.service_config.es_backend,
    url=settings.service_config.es_url
)

# RDB 客户端（暂时保持原样）
rdb_client = RDBClient(url=settings.service_config.rdb_url) if settings.service_config.rdb_url else None

__all__ = ["es_client", "rdb_client"]
