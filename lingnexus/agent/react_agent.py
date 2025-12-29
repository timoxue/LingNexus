"""
ReActAgent 便捷函数
提供快速创建常用 Agent 的函数
"""

from typing import Optional
from agentscope.agent import ReActAgent

from ..config.model_config import create_model, get_formatter, ModelType
from .agent_factory import AgentFactory


def create_docx_agent(
    model_type: ModelType | str = ModelType.QWEN,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.5,
) -> ReActAgent:
    """
    快速创建支持 docx 技能的 Agent
    
    Args:
        model_type: 模型类型（"qwen" 或 "deepseek"）
        model_name: 模型名称
        api_key: API Key
        temperature: 温度参数
    
    Returns:
        ReActAgent 实例
    
    Examples:
        >>> agent = create_docx_agent(model_type="qwen")
        >>> response = agent.call("请创建一个新的 Word 文档")
    """
    factory = AgentFactory()
    return factory.create_docx_agent(
        model_type=model_type,
        model_name=model_name,
        api_key=api_key,
        temperature=temperature,
    )

