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


def create_progressive_agent(
    model_name: str = "qwen-max",
    skill_type: str = "external",
    temperature: float = 0.3,
    api_key: Optional[str] = None,
    max_tokens: int = 4096,
    system_prompt: Optional[str] = None,
) -> ReActAgent:
    """
    创建支持渐进式披露的 Agent（使用 qwen-max 作为 orchestrator）
    
    实现 Claude Skills 的渐进式披露机制：
    - 阶段1：初始化时只加载所有 Skills 的元数据（~100 tokens/Skill）
    - 阶段2：LLM 判断需要时，动态加载完整指令（~5k tokens）
    - 阶段3：按需访问资源文件（scripts/, references/, assets/）
    
    Args:
        model_name: 模型名称，默认 "qwen-max"
        skill_type: 技能类型，默认 "external"
        temperature: 温度参数，默认 0.3（orchestrator 建议较低温度）
        api_key: API Key
        max_tokens: 最大生成 token 数，默认 4096
        system_prompt: 自定义系统提示词
    
    Returns:
        ReActAgent 实例
    
    Examples:
        >>> import asyncio
        >>> from agentscope.message import Msg
        >>> agent = create_progressive_agent(model_name="qwen-max")
        >>> response = await agent(Msg(name="user", content="创建一个 Word 文档"))
    """
    factory = AgentFactory()
    return factory.create_progressive_agent(
        model_type=ModelType.QWEN,
        model_name=model_name,
        skill_type=skill_type,
        temperature=temperature,
        api_key=api_key,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
    )

