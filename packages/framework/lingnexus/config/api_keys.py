"""
API Key 管理模块
支持多种方式管理 API Keys：环境变量、.env 文件、配置文件
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


# 尝试加载 .env 文件
_env_file = Path(".env")
if _env_file.exists():
    load_dotenv(_env_file)


def get_dashscope_api_key(api_key: Optional[str] = None) -> Optional[str]:
    """
    获取 DashScope API Key（用于 Qwen 和 DeepSeek）
    
    优先级：
    1. 函数参数传入的 api_key
    2. 环境变量 DASHSCOPE_API_KEY
    3. .env 文件中的 DASHSCOPE_API_KEY
    4. 返回 None
    
    Args:
        api_key: 直接传入的 API Key（优先级最高）
    
    Returns:
        API Key 字符串，如果都未设置则返回 None
    
    Examples:
        >>> key = get_dashscope_api_key()
        >>> key = get_dashscope_api_key("sk-xxx")  # 直接传入
    """
    # 优先级 1: 函数参数
    if api_key:
        return api_key
    
    # 优先级 2: 环境变量
    key = os.getenv("DASHSCOPE_API_KEY")
    if key:
        return key
    
    # 优先级 3: .env 文件（已通过 load_dotenv 加载）
    # 如果 .env 文件存在，上面的 load_dotenv 已经加载了
    # 这里再次检查（以防 load_dotenv 之后环境变量被设置）
    key = os.getenv("DASHSCOPE_API_KEY")
    if key:
        return key
    
    return None


def require_dashscope_api_key(api_key: Optional[str] = None) -> str:
    """
    获取 DashScope API Key，如果未设置则抛出异常
    
    Args:
        api_key: 直接传入的 API Key
    
    Returns:
        API Key 字符串
    
    Raises:
        ValueError: 如果 API Key 未设置
    
    Examples:
        >>> key = require_dashscope_api_key()  # 从环境变量读取
        >>> key = require_dashscope_api_key("sk-xxx")  # 直接传入
    """
    key = get_dashscope_api_key(api_key)
    if not key:
        raise ValueError(
            "DashScope API Key 未设置。请使用以下方式之一设置：\n"
            "1. 设置环境变量: export DASHSCOPE_API_KEY=your_key\n"
            "2. 创建 .env 文件: DASHSCOPE_API_KEY=your_key\n"
            "3. 在代码中传入: create_model(..., api_key='your_key')"
        )
    return key

