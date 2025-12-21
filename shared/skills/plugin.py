"""插件包装标准：为 Skill 开发者提供标准化的插件开发工具。

本模块提供：
1. BasePlugin 基类：标准化插件开发模式；
2. plugin_entrypoint 装饰器：简化入口函数定义；
3. 类型提示与验证工具：提升开发体验。

使用方式 1 - 基于类的插件（推荐用于复杂插件）：
    from shared.skills.plugin import BasePlugin

    class MyPlugin(BasePlugin):
        async def execute(self, payload: dict, context: dict | None = None) -> dict:
            # 实现插件逻辑
            return {"status": "success", "data": ...}

使用方式 2 - 基于函数的插件（推荐用于简单插件）：
    from shared.skills.plugin import plugin_entrypoint

    @plugin_entrypoint
    async def run_plugin(payload: dict, context: dict | None = None) -> dict:
        # 实现插件逻辑
        return {"status": "success", "data": ...}
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from functools import wraps
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Optional

from pydantic import BaseModel, ValidationError

from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

# 插件入口函数的标准签名类型
PluginEntrypoint = Callable[[Dict[str, Any], Optional[Dict[str, Any]]], Awaitable[Dict[str, Any]]]


class PluginContext(BaseModel):
    """插件执行上下文（可选传入）。

    提供运行时环境信息，便于插件访问用户身份、租户信息、会话 ID 等。
    """

    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    session_id: Optional[str] = None
    trace_id: Optional[str] = None
    extra: Dict[str, Any] = {}


class PluginResult(BaseModel):
    """插件执行结果的标准化包装。

    推荐插件返回此结构，便于统一处理成功/失败状态。
    """

    status: str  # "success" | "error" | "partial"
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BasePlugin(ABC):
    """插件基类，提供标准化的插件开发模式。

    子类需要实现 execute() 方法，定义插件的核心逻辑。
    Runtime 会调用 __call__() 方法，自动包装日志、异常处理等。

    示例：
        class DailyDigestPlugin(BasePlugin):
            async def execute(self, payload: dict, context: dict | None = None) -> dict:
                topics = payload.get("topics", [])
                role = payload.get("role", "general")
                # ... 调用 Skill 完成业务逻辑
                return {"status": "success", "output": {...}}
    """

    def __init__(self, plugin_id: str | None = None):
        """初始化插件实例。

        Args:
            plugin_id: 插件唯一 ID（通常从 manifest 读取）
        """
        self.plugin_id = plugin_id
        self.logger = get_logger(f"plugin.{plugin_id or 'unknown'}")

    @abstractmethod
    async def execute(self, payload: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """插件核心逻辑（必须由子类实现）。

        Args:
            payload: 插件输入参数（应与 manifest 中的 input_schema 对应）
            context: 可选的执行上下文（用户、租户、会话等信息）

        Returns:
            插件输出结果（应与 manifest 中的 output_schema 对应）
        """
        raise NotImplementedError

    async def __call__(self, payload: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Runtime 调用入口（自动包装日志、异常处理）。

        这是 Plugin Runtime 实际调用的方法，不建议子类重写。
        """
        self.logger.info(
            "Plugin execution started",
            extra={
                "plugin_id": self.plugin_id,
                "payload_keys": list(payload.keys()),
            },
        )

        try:
            result = await self.execute(payload, context)
            self.logger.info(
                "Plugin execution completed",
                extra={"plugin_id": self.plugin_id, "status": result.get("status", "unknown")},
            )
            return result

        except Exception as exc:
            self.logger.error(
                "Plugin execution failed",
                extra={
                    "plugin_id": self.plugin_id,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
            )
            # 返回标准错误结构
            return {
                "status": "error",
                "error": str(exc),
                "error_type": type(exc).__name__,
            }


def plugin_entrypoint(func: PluginEntrypoint) -> PluginEntrypoint:
    """装饰器：为简单函数式插件提供标准化包装。

    自动添加日志记录和异常处理，无需显式继承 BasePlugin。

    示例：
        @plugin_entrypoint
        async def run_plugin(payload: dict, context: dict | None = None) -> dict:
            # 插件逻辑
            return {"status": "success", "data": ...}
    """

    @wraps(func)
    async def wrapper(payload: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        func_logger = get_logger(f"plugin.{func.__module__}.{func.__name__}")
        func_logger.info(
            "Plugin function started",
            extra={
                "function": func.__name__,
                "payload_keys": list(payload.keys()),
            },
        )

        try:
            result = await func(payload, context)
            func_logger.info(
                "Plugin function completed",
                extra={"function": func.__name__, "status": result.get("status", "unknown")},
            )
            return result

        except Exception as exc:
            func_logger.error(
                "Plugin function failed",
                extra={
                    "function": func.__name__,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
            )
            return {
                "status": "error",
                "error": str(exc),
                "error_type": type(exc).__name__,
            }

    return wrapper


def load_manifest(plugin_dir: Path) -> Dict[str, Any]:
    """从插件目录加载 plugin_manifest.json。

    Args:
        plugin_dir: 插件根目录路径

    Returns:
        解析后的 manifest 字典

    Raises:
        FileNotFoundError: manifest 文件不存在
        json.JSONDecodeError: manifest 格式错误
    """
    manifest_path = plugin_dir / "plugin_manifest.json"
    if not manifest_path.exists():
        msg = f"plugin_manifest.json not found in {plugin_dir}"
        raise FileNotFoundError(msg)

    with manifest_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_manifest(manifest: Dict[str, Any]) -> bool:
    """验证 manifest 是否符合标准格式。

    Args:
        manifest: manifest 字典

    Returns:
        True 表示验证通过

    Raises:
        ValidationError: 字段缺失或格式错误
    """
    required_fields = [
        "plugin_id",
        "version",
        "name",
        "description",
        "author",
        "category",
        "entrypoint",
        "input_schema",
        "output_schema",
    ]

    missing_fields = [field for field in required_fields if field not in manifest]
    if missing_fields:
        msg = f"Missing required fields in manifest: {', '.join(missing_fields)}"
        raise ValidationError(msg)

    return True


# 便捷导出
__all__ = [
    "BasePlugin",
    "PluginContext",
    "PluginResult",
    "PluginEntrypoint",
    "plugin_entrypoint",
    "load_manifest",
    "validate_manifest",
]
