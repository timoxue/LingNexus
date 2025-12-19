from core_agents.rd_service.schema import RDRequest, RDResponse
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


async def run_rd_pipeline(request: RDRequest) -> RDResponse:
    """药物研发服务主流程（骨架）。"""
    logger.info("RD pipeline called", extra={"compound": request.compound})
    # TODO: 实现药物研发流程逻辑
    return RDResponse(
        summary="药物研发骨架结果",
        predictions=["预测1（待实现）", "预测2（待实现）"],
    )
