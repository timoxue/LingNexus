from fastapi import Depends, FastAPI

from config.settings import settings
from core_agents.intelligence_service.schema import (
    IntelligenceRequest,
    IntelligenceResponse,
    DailyDigestRequest,
    DailyDigestResponse,
)
from core_agents.intelligence_service.workflows.intel_workflow import (
    run_intelligence_pipeline,
)
from core_agents.intelligence_service.workflows.daily_digest_workflow import (
    run_daily_digest,
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


@app.post(
    "/v1/internal/daily_digest",
    response_model=DailyDigestResponse,
    summary="生成情报订阅日报（内部接口）",
    tags=["internal"],
)
async def generate_daily_digest(
    request: DailyDigestRequest,
    _settings=Depends(get_settings),
) -> DailyDigestResponse:
    """根据主题列表和用户列表生成订阅日报。

    该接口主要用于 n8n 等编排工具的内部调用，不直接面向外部用户。
    """

    logger.info(
        "Received daily digest request",
        extra={"topic_count": len(request.topics or []), "user_count": len(request.users or [])},
    )
    result = await run_daily_digest(request)
    return result
