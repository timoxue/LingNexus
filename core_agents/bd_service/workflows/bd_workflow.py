from core_agents.bd_service.schema import BDRequest, BDResponse
from shared.skills import get_skill
from shared.skills.bd.lead_qualification import BDLeadQualificationInput
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


async def run_bd_pipeline(request: BDRequest) -> BDResponse:
    """BD 服务主流程：调用 BD 相关技能完成线索评估。"""
    logger.info("BD pipeline called", extra={"target": request.target})

    skill = get_skill("bd.lead_qualification")
    if skill is not None:
        skill_input = BDLeadQualificationInput(target=request.target, context=request.context)
        skill_output = await skill.execute(skill_input)
        summary = str(skill_output.data) if skill_output.success else "BD 分析失败，请检查日志"
        recommendations = []
    else:
        # 暂无技能实现时的降级行为
        summary = "BD 分析骨架结果"
        recommendations = ["建议1（待实现）", "建议2（待实现）"]

    return BDResponse(summary=summary, recommendations=recommendations)
