from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def verify_api_key(api_key: str) -> bool:
    """API Key 鉴权（骨架）。

    后续可对接 JWT、OAuth2 等。
    """
    logger.info("Verifying API key")
    # TODO: 实现真实鉴权逻辑
    return True
