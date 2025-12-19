from fastapi import Depends, FastAPI

from config.settings import settings
from core_agents.bd_service.schema import BDRequest, BDResponse
from core_agents.bd_service.workflows.bd_workflow import run_bd_pipeline
from shared.utils.logging_utils import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="BD Service",
    description="BD 流程服务（第一期骨架）",
    version="0.1.0",
)


def get_settings():
    return settings


@app.post(
    "/bd/analyze",
    response_model=BDResponse,
    summary="BD 分析",
    tags=["bd"],
)
async def analyze_bd(
    request: BDRequest,
    _settings=Depends(get_settings),
) -> BDResponse:
    """BD 流程分析接口（骨架）。"""
    logger.info("Received BD request", extra={"target": request.target})
    result = await run_bd_pipeline(request)
    return result
