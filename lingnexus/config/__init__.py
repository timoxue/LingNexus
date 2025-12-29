"""
配置模块
提供模型配置和 Agent 配置功能

注意：
- 模型配置：使用 model_config.py（直接实例化模型）
- 全局配置：使用 agent_config.py（agentscope.init()）
"""

from .model_config import create_model, get_formatter, ModelType
from .agent_config import init_agentscope
from .api_keys import get_dashscope_api_key, require_dashscope_api_key

__all__ = [
    "create_model",
    "get_formatter",
    "ModelType",
    "init_agentscope",
    "get_dashscope_api_key",
    "require_dashscope_api_key",
]

