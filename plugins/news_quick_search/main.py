"""新闻快速搜索插件入口。

本插件展示如何将底层 Skill (FetchNewsSkill) 包装为面向用户的插件。

核心思想：
1. 插件不重复实现业务逻辑
2. 通过 get_skill() 获取已注册的 Skill
3. 调用 Skill 的 execute() 方法
4. 将结果转换为用户友好的格式
"""

from typing import Any, Dict, Optional

from shared.skills.plugin import plugin_entrypoint
from shared.skills.registry import get_skill
from shared.skills.intelligence.fetch_news import FetchNewsInput
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


@plugin_entrypoint
async def run_plugin(payload: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """新闻快速搜索插件入口函数。

    Args:
        payload: 用户输入参数，包含：
            - topic_name (str, required): 搜索主题
            - keywords (list[str], optional): 关键词列表
            - max_items (int, optional): 最大返回数量，默认10

        context: 运行时上下文（可选），包含：
            - user_id: 用户ID
            - trace_id: 追踪ID
            - session_id: 会话ID

    Returns:
        包含搜索结果的字典：
        {
            "status": "success" | "error",
            "news_count": int,
            "news_items": [...],
            "error": str (仅在失败时)
        }

    示例输入：
        {
            "topic_name": "PD-1 肺癌",
            "keywords": ["PD-1", "NSCLC", "免疫治疗"],
            "max_items": 5
        }
    """

    # 1. 提取和验证输入参数
    topic_name = payload.get("topic_name")
    if not topic_name:
        return {
            "status": "error",
            "error": "缺少必需参数：topic_name",
            "news_count": 0,
            "news_items": []
        }

    keywords = payload.get("keywords", [])
    max_items = payload.get("max_items", 10)

    # 添加详细日志：查看收到的原始参数
    logger.info(
        "News search plugin started - RAW PARAMS",
        extra={
            "raw_payload": payload,
            "topic_type": type(topic_name).__name__,
            "keywords_type": type(keywords).__name__,
            "keywords_value": keywords,
            "keywords_count": len(keywords) if isinstance(keywords, list) else 0,
        }
    )

    # 2. 获取底层 Skill（关键步骤！）
    fetch_news_skill = get_skill("intel.fetch_news")
    if not fetch_news_skill:
        logger.error("Required skill 'intel.fetch_news' not found")
        return {
            "status": "error",
            "error": "系统错误：新闻检索服务不可用",
            "news_count": 0,
            "news_items": []
        }

    # 3. 构造 Skill 的输入对象
    skill_input = FetchNewsInput(
        topic_name=topic_name,
        keywords=keywords,
        max_items=max_items
    )

    # 4. 调用 Skill 执行业务逻辑
    try:
        skill_output = await fetch_news_skill.execute(skill_input)

        if not skill_output.success:
            logger.warning(
                "Skill execution failed",
                extra={"message": skill_output.message}
            )
            return {
                "status": "error",
                "error": skill_output.message,
                "news_count": 0,
                "news_items": []
            }

        # 5. 转换为用户友好的输出格式
        news_items = skill_output.data or []
        
        logger.info(
            "News search completed",
            extra={
                "topic": topic_name,
                "count": len(news_items)
            }
        )

        return {
            "status": "success",
            "news_count": len(news_items),
            "news_items": news_items,
            "topic": topic_name,
            "keywords": keywords
        }

    except Exception as e:
        logger.error(
            "Plugin execution failed",
            extra={
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        return {
            "status": "error",
            "error": f"执行失败: {str(e)}",
            "news_count": 0,
            "news_items": []
        }
