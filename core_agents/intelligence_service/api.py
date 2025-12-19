from fastapi import Depends, FastAPI

from config.settings import settings
from core_agents.intelligence_service.schema import (
    IntelligenceRequest,
    IntelligenceResponse,
)
from core_agents.intelligence_service.workflows.intel_workflow import (
    run_intelligence_pipeline,
)
from shared.utils.logging_utils import setup_logging, get_logger

# 初始化日志
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Intelligence Service",
    description="情报分析服务（第一期原型）",
    version="0.1.0",
)


def get_settings():
    return settings


@app.post(
    "/intelligence/analyze",
    response_model=IntelligenceResponse,
    summary="情报分析",
    tags=["intelligence"],
)
async def analyze_intelligence(
    request: IntelligenceRequest,
    _settings=Depends(get_settings),
) -> IntelligenceResponse:
    """基于大模型的情报分析接口。"""

    logger.info("Received intelligence request", extra={"query": request.query})
    result = await run_intelligence_pipeline(request)
    return result
