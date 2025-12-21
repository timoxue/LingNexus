"""订阅日报 Quick Run 插件入口（使用插件标准基类）。

本文件展示如何使用 shared.skills.plugin 提供的标准化工具开发插件。

注意：当前版本仍保持原有的函数式入口 run_plugin()，确保向后兼容。
     未来可以考虑迁移到 BasePlugin 类模式。
"""

from typing import Any, Dict, List, Optional

from core_agents.intelligence_service.schema import (
    DailyDigestRequest,
    DailyDigestResponse,
    TopicConfig,
    UserConfig,
)
from core_agents.intelligence_service.workflows.daily_digest_workflow import run_daily_digest
from shared.skills.plugin import plugin_entrypoint
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


@plugin_entrypoint
async def run_plugin(input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """订阅日报 Quick Run 插件入口（使用标准装饰器包装）。

    Args:
        input_data: 调用方传入的参数，应与 plugin_manifest.json 中的 input_schema 对齐。
                   必需字段：
                   - topics: array of {name, keywords?, max_items?}
                   - role: "bd" | "med" | "market" | "rd" | "general"
        context:    运行时上下文（可选），例如当前用户、trace_id 等。

    Returns:
        符合 output_schema 的结果字典，结构与 DailyDigestResponse 对齐。
        
    示例输入：
        {
          "topics": [
            {
              "name": "PD-1 肺癌",
              "keywords": ["PD-1", "NSCLC", "免疫治疗"],
              "max_items": 5
            }
          ],
          "role": "bd"
        }
    """

    topics_input = input_data.get("topics") or []
    role = input_data.get("role") or "bd"

    # 转换为 TopicConfig 列表
    topics: List[TopicConfig] = []
    for idx, t in enumerate(topics_input):
        # plugin manifest 中 topic_id 可选，这里兜底生成
        topic_id = t.get("topic_id") or f"plugin_topic_{idx + 1}"
        topic = TopicConfig(
            topic_id=topic_id,
            name=t["name"],
            description=t.get("description"),
            keywords=t.get("keywords") or [],
            max_items=t.get("max_items") or 5,
        )
        topics.append(topic)

    if not topics:
        # 没有传入任何主题，返回空结果
        logger.warning("No topics provided in plugin input")
        empty_response = DailyDigestResponse(task_id="", status="empty", items=[])
        return empty_response.model_dump()

    # 构造一个简化的用户列表：单一用户，订阅所有主题，角色由 input_data.role 决定
    user = UserConfig(
        user_id=context.get("user_id", "plugin_user") if context else "plugin_user",
        email=None,
        subscribed_topics=[t.topic_id for t in topics],
        role=role,
    )

    request = DailyDigestRequest(topics=topics, users=[user])

    logger.info(
        "DailyDigest plugin executing",
        extra={
            "topic_count": len(topics),
            "role": role,
            "user_id": user.user_id,
        },
    )

    # 调用底层 Workflow
    response: DailyDigestResponse = await run_daily_digest(request)

    logger.info(
        "DailyDigest plugin execution completed",
        extra={
            "task_id": response.task_id,
            "status": response.status,
            "items_count": len(response.items),
        },
    )

    # 返回 Pydantic 模型的 dict 表达
    # @plugin_entrypoint 装饰器会自动处理异常和日志
    return response.model_dump()
