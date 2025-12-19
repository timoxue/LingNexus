from typing import List

from core_agents.intelligence_service.schema import (
    IntelligenceRequest,
    IntelligenceResponse,
    IntelligenceSource,
)
from shared.models.llm_manager import llm_manager
from shared.prompts.manager import prompt_manager
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


async def run_intelligence_pipeline(request: IntelligenceRequest) -> IntelligenceResponse:
    """情报服务主流程（使用统一 Prompt 管理）。"""

    # 选择 Prompt 版本（可根据请求复杂度、长度等动态选择）
    # 默认使用基础版，后续可根据业务需要扩展
    prompt_key = "intelligence_summary_v1"
    
    # 渲染 Prompt
    prompt_text = prompt_manager.render(
        service="intelligence",
        key=prompt_key,
        query=request.query,
        context=request.context or "无额外上下文",
    )
    
    # 获取推荐模型（也可以使用默认模型）
    recommended_model = prompt_manager.get_recommended_model("intelligence", prompt_key)
    
    logger.info(
        "Intelligence pipeline started",
        extra={
            "query": request.query,
            "prompt_key": prompt_key,
            "recommended_model": recommended_model,
        }
    )

    # 构造消息
    messages = [
        {"role": "system", "content": prompt_text},
        {"role": "user", "content": "请按上述要求输出结果。"},
    ]

    # 调用大模型（使用推荐模型）
    raw_answer = await llm_manager.chat(messages, model_name=recommended_model)

    # 解析响应（简单处理，后续可优化）
    lines = [line.strip() for line in raw_answer.splitlines() if line.strip()]
    if not lines:
        return IntelligenceResponse(summary="未能生成有效结论", key_points=[], sources=[])

    summary = lines[0]
    key_points = lines[1:8]

    return IntelligenceResponse(
        summary=summary,
        key_points=key_points,
        sources=[],  # 第一版暂不返回真实来源
    )
