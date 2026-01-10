"""
模型配置模块
支持 DeepSeek 和 Qwen (DashScope) 模型

注意：
- ReActAgent 需要直接传入模型实例，不支持通过 agentscope.init() 配置
- 因此我们提供直接创建模型实例的函数
- 如果需要全局配置（日志、Studio等），可以在应用启动时调用 agentscope.init()
"""

import os
from enum import Enum
from typing import Optional
from agentscope.model import DashScopeChatModel
from agentscope.formatter import DashScopeChatFormatter

from .api_keys import get_dashscope_api_key


class ModelType(str, Enum):
    """支持的模型类型"""
    QWEN = "qwen"  # 通义千问（通过 DashScope）
    DEEPSEEK = "deepseek"  # DeepSeek（通过 DashScope）


def create_qwen_model(
    model_name: str = "qwen-max",
    api_key: Optional[str] = None,
    temperature: float = 0.5,
    max_tokens: int = 2048,
) -> DashScopeChatModel:
    """
    创建 Qwen（通义千问）模型实例
    
    Args:
        model_name: 模型名称，如 "qwen-max", "qwen-plus", "qwen-turbo"
        api_key: API Key，如果不提供则从环境变量 DASHSCOPE_API_KEY 读取
        temperature: 温度参数，控制输出的随机性
        max_tokens: 最大生成 token 数
    
    Returns:
        DashScopeChatModel 实例
    """
    return DashScopeChatModel(
        model_name=model_name,
        api_key=get_dashscope_api_key(api_key),
        generate_kwargs={
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    )


def create_deepseek_model(
    model_name: str = "deepseek-chat",
    api_key: Optional[str] = None,
    temperature: float = 0.5,
    max_tokens: int = 2048,
) -> DashScopeChatModel:
    """
    创建 DeepSeek 模型实例
    
    Args:
        model_name: 模型名称，如 "deepseek-chat", "deepseek-coder"
        api_key: API Key，如果不提供则从环境变量 DASHSCOPE_API_KEY 读取
        temperature: 温度参数，控制输出的随机性
        max_tokens: 最大生成 token 数
    
    Returns:
        DashScopeChatModel 实例
    """
    return DashScopeChatModel(
        model_name=model_name,
        api_key=get_dashscope_api_key(api_key),
        generate_kwargs={
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    )


def create_model(
    model_type: ModelType | str,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.5,
    max_tokens: int = 2048,
):
    """
    创建模型实例的统一接口
    
    Args:
        model_type: 模型类型（"qwen" 或 "deepseek"）
        model_name: 模型名称，如果不提供则使用默认值
        api_key: API Key
        temperature: 温度参数
        max_tokens: 最大生成 token 数
    
    Returns:
        模型实例
    
    Examples:
        >>> model = create_model("qwen", model_name="qwen-max")
        >>> model = create_model(ModelType.DEEPSEEK, temperature=0.7)
    """
    model_type = ModelType(model_type.lower()) if isinstance(model_type, str) else model_type
    
    if model_type == ModelType.QWEN:
        default_name = model_name or "qwen-max"
        return create_qwen_model(
            model_name=default_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    elif model_type == ModelType.DEEPSEEK:
        default_name = model_name or "deepseek-chat"
        return create_deepseek_model(
            model_name=default_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")


def get_formatter(model_type: ModelType | str = ModelType.QWEN):
    """
    根据模型类型获取对应的 formatter
    
    Args:
        model_type: 模型类型（"qwen" 或 "deepseek"）
    
    Returns:
        Formatter 实例
    """
    # Qwen 和 DeepSeek 都使用 DashScope 的 API，所以使用相同的 formatter
    return DashScopeChatFormatter()

