from __future__ import annotations

from typing import Any, Dict, Optional

from plugin_runtime.plugin_loader import PluginEntrypoint
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


async def run_plugin_sandboxed(
    entrypoint: PluginEntrypoint,
    payload: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """在沙箱中执行插件入口函数。

    当前阶段为 MVP 实现：
    - 直接在同一进程内调用入口函数；
    - 预留未来扩展点（多进程/容器隔离、资源配额、超时控制等）。
    """

    # TODO: 后续可以在这里增加超时控制、审计日志、资源隔离等能力
    return await entrypoint(payload, context=context)
