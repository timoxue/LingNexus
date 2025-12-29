"""
LingNexus - 基于 AgentScope 的多智能体系统
支持 Claude Skills 兼容
"""

__version__ = "0.1.0"

# 导出 CLI 工具
from .cli import InteractiveTester

__all__ = ["InteractiveTester"]

