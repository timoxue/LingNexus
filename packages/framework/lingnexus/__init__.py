"""
LingNexus Framework
多智能体系统框架，支持渐进式披露机制
"""

__version__ = "0.2.0"

# 核心 API
from .agent_factory import AgentFactory
from .react_agent import create_docx_agent, create_progressive_agent

# 存储模块
try:
    from .storage import RawStorage, StructuredDB
except ImportError:
    RawStorage = None
    StructuredDB = None

# 调度模块
try:
    from .scheduler import DailyMonitoringTask
except ImportError:
    DailyMonitoringTask = None

# 兼容性导入：保持向后兼容
try:
    from .utils.skill_loader import SkillLoader
except ImportError:
    try:
        from .skill import SkillLoader
    except ImportError:
        SkillLoader = None

__all__ = [
    "AgentFactory",
    "create_docx_agent",
    "create_progressive_agent",
    "RawStorage",
    "StructuredDB",
    "DailyMonitoringTask",
    "SkillLoader",
]

