from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

from plugin_runtime.models import PluginManifest
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

# 插件入口函数签名：接收 payload 和可选 context，返回异步结果
PluginEntrypoint = Callable[[Dict[str, Any], Optional[Dict[str, Any]]], Awaitable[Dict[str, Any]]]


def get_plugins_dir() -> Path:
    """返回插件根目录路径。

    当前约定：插件位于项目根目录下的 ``plugins/`` 目录中。
    """

    return Path(__file__).resolve().parent.parent / "plugins"


def discover_manifests() -> List[PluginManifest]:
    """扫描插件目录并返回所有合法的 PluginManifest 列表。

    - 忽略解析失败的 manifest（仅记录日志，不中断整体加载流程）。
    """

    plugins_dir = get_plugins_dir()
    if not plugins_dir.exists():
        logger.warning("Plugins directory does not exist", extra={"dir": str(plugins_dir)})
        return []

    manifests: List[PluginManifest] = []

    for manifest_path in plugins_dir.rglob("plugin_manifest.json"):
        try:
            with manifest_path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            manifest = PluginManifest(**raw)
            manifests.append(manifest)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Failed to load plugin manifest",
                extra={"path": str(manifest_path), "error": str(exc)},
            )
            continue

    return manifests


def load_entrypoint(manifest: PluginManifest) -> Optional[PluginEntrypoint]:
    """根据 manifest.entrypoint 导入插件入口函数。

    入口格式约定为 ``"package.module:attr"``，例如：
    ``"plugins.intel_daily_digest.main:run_plugin"``。
    """

    try:
        module_path, attr_name = manifest.entrypoint.split(":", 1)
        module = importlib.import_module(module_path)
        entrypoint = getattr(module, attr_name)
        return entrypoint  # type: ignore[return-value]
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Failed to import plugin entrypoint",
            extra={"plugin_id": manifest.plugin_id, "entrypoint": manifest.entrypoint, "error": str(exc)},
        )
        return None
