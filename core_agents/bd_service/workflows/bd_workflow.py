from core_agents.bd_service.schema import BDRequest, BDResponse
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


async def run_bd_pipeline(request: BDRequest) -> BDResponse:
    """BD 服务主流程（骨架）。"""
    logger.info("BD pipeline called", extra={"target": request.target})
    # TODO: 实现 BD 流程逻辑
    return BDResponse(
        summary="BD 分析骨架结果",
        recommendations=["建议1（待实现）", "建议2（待实现）"],
    )
