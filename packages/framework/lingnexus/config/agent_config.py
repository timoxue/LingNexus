"""
Agent 全局配置模块
提供 agentscope.init() 的封装，用于全局配置（日志、Studio等）

注意：不用于模型配置，模型配置请使用 model_config.py
"""

import os
import sys
import logging
import agentscope
from typing import Optional

logger = logging.getLogger(__name__)

# Windows 编码修复：设置环境变量，确保子进程使用 UTF-8 编码
if sys.platform == 'win32':
    # 确保子进程使用 UTF-8 编码（AgentScope 的 subprocess 会继承此设置）
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    os.environ.setdefault('PYTHONLEGACYWINDOWSSTDIO', '0')

# 默认 AgentScope Studio URL
DEFAULT_STUDIO_URL = "http://localhost:3000"


def init_agentscope(
    project: Optional[str] = "LingNexus",
    name: Optional[str] = None,
    run_id: Optional[str] = None,
    logging_path: Optional[str] = "./logs",
    logging_level: str = "INFO",
    studio_url: Optional[str] = DEFAULT_STUDIO_URL,
    tracing_url: Optional[str] = None,
) -> None:
    """
    初始化 AgentScope 全局配置

    注意：此函数用于全局配置（日志、Studio等），不用于模型配置。
    模型配置请使用 model_config.py 中的函数。

    Args:
        project: 项目名称
        name: 运行名称
        run_id: 运行 ID
        logging_path: 日志保存路径
        logging_level: 日志级别
        studio_url: AgentScope Studio URL（默认 http://localhost:3000）
        tracing_url: 追踪 URL

    Examples:
        >>> from lingnexus.config.agent_config import init_agentscope
        >>> init_agentscope(project="MyProject", logging_path="./logs")

    Studio 禁用:
        >>> init_agentscope(studio_url=None)  # 不连接 Studio
    """
    logger.info(f"Initializing AgentScope with project='{project}', studio_url='{studio_url}'")

    agentscope.init(
        project=project,
        name=name,
        run_id=run_id,
        logging_path=logging_path,
        logging_level=logging_level,
        studio_url=studio_url,
        tracing_url=tracing_url,
    )

    logger.info(f"AgentScope initialized successfully")
    if studio_url:
        logger.info(f"AgentScope Studio monitoring enabled at: {studio_url}")
        logger.info(f"Project name in Studio: {project}")
    else:
        logger.warning(f"AgentScope Studio monitoring DISABLED (studio_url=None)")

