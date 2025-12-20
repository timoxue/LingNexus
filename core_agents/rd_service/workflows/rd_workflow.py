from core_agents.rd_service.schema import RDRequest, RDResponse
from shared.skills import get_skill
from shared.skills.rd.compound_analysis import RDCompoundAnalysisInput
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


async def run_rd_pipeline(request: RDRequest) -> RDResponse:
    """药物研发服务主流程：调用 RD 相关技能完成分析。"""
    logger.info("RD pipeline called", extra={"compound": request.compound})

    skill = get_skill("rd.compound_analysis")
    if skill is not None:
        skill_input = RDCompoundAnalysisInput(compound=request.compound, context=request.context)
        skill_output = await skill.execute(skill_input)
        summary = str(skill_output.data) if skill_output.success else "药物研发分析失败，请检查日志"
        predictions = []
    else:
        # 暂无技能实现时的降级行为
        summary = "药物研发骨架结果"
        predictions = ["预测1（待实现）", "预测2（待实现）"]

    return RDResponse(summary=summary, predictions=predictions)
