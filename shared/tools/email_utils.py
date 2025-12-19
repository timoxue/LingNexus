from typing import List

from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


async def send_email(to: List[str], subject: str, body: str) -> bool:
    """发送邮件工具（骨架）。"""
    logger.info("Sending email", extra={"to": to, "subject": subject})
    # TODO: 接入 SMTP 或第三方邮件服务
    return True
