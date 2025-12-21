import logging
from typing import Optional


def setup_logging(level: str = "INFO") -> None:
    """简单的全局 logging 配置。"""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )

    # 兼容性处理：避免第三方 logger 使用 extra={"name": ...} 时覆盖 LogRecord 内置字段
    # 导致 "Attempt to overwrite 'name' in LogRecord" 这类异常，统一在这里做一次清洗。
    old_makeRecord = logging.Logger.makeRecord

    def safe_makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):  # type: ignore[override]
        if extra and "name" in extra:
            extra = dict(extra)
            extra.pop("name", None)
        return old_makeRecord(self, name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)

    logging.Logger.makeRecord = safe_makeRecord


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or __name__)
