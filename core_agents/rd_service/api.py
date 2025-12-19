from fastapi import Depends, FastAPI

from config.settings import settings
from core_agents.rd_service.schema import RDRequest, RDResponse
from core_agents.rd_service.workflows.rd_workflow import run_rd_pipeline
from shared.utils.logging_utils import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="RD Service",
    description="药物研发服务（第一期骨架）",
    version="0.1.0",
)


def get_settings():
    return settings


@app.post(
    "/rd/analyze",
    response_model=RDResponse,
    summary="药物研发分析",
    tags=["rd"],
)
async def analyze_rd(
    request: RDRequest,
    _settings=Depends(get_settings),
) -> RDResponse:
    """药物研发分析接口（骨架）。"""
    logger.info("Received RD request", extra={"compound": request.compound})
    result = await run_rd_pipeline(request)
    return result
