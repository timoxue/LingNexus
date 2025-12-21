from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

from plugin_runtime.models import PluginManifest
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

PluginEntrypoint = Callable[[Dict[str, Any], Optional[Dict[str, Any]]], Awaitable[Dict[str, Any]]]

_PLUGINS: Dict[str, PluginManifest] = {}
_ENTRYPOINTS: Dict[str, PluginEntrypoint] = {}


def _get_plugins_dir() -> Path:
    """返回插件根目录路径。

    当前约定：插件位于项目根目录下的 ``plugins/`` 目录中。
    """

    return Path(__file__).resolve().parent.parent / "plugins"


def load_plugins() -> None:
    """从 plugins 目录加载插件 manifest 并初始化入口函数。

    对于 MVP，实现简单遍历 ``plugin_manifest.json`` 的加载逻辑，仅要保证
    订阅日报插件可以被发现和调用即可。
    """

    plugins_dir = _get_plugins_dir()
    if not plugins_dir.exists():
        logger.warning("Plugins directory does not exist", extra={"dir": str(plugins_dir)})
        return

    for manifest_path in plugins_dir.rglob("plugin_manifest.json"):
        try:
            with manifest_path.open("r", encoding="utf-8") as f:
                raw = json.load(f)
            manifest = PluginManifest(**raw)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Failed to load plugin manifest",
                extra={"path": str(manifest_path), "error": str(exc)},
            )
            continue

        plugin_id = manifest.plugin_id
        _PLUGINS[plugin_id] = manifest

        try:
            module_path, attr_name = manifest.entrypoint.split(":", 1)
            module = importlib.import_module(module_path)
            entrypoint = getattr(module, attr_name)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Failed to import plugin entrypoint",
                extra={"plugin_id": plugin_id, "entrypoint": manifest.entrypoint, "error": str(exc)},
            )
            continue

        _ENTRYPOINTS[plugin_id] = entrypoint  # type: ignore[assignment]
        logger.info(
            "Plugin loaded",
            extra={"plugin_id": plugin_id, "entrypoint": manifest.entrypoint},
        )


def list_manifests() -> List[PluginManifest]:
    """返回所有已加载的插件 manifest 列表。"""

    return list(_PLUGINS.values())


def get_manifest(plugin_id: str) -> Optional[PluginManifest]:
    """根据 plugin_id 获取插件 manifest。"""

    return _PLUGINS.get(plugin_id)


def get_entrypoint(plugin_id: str) -> Optional[PluginEntrypoint]:
    """根据 plugin_id 获取插件入口函数。"""

    return _ENTRYPOINTS.get(plugin_id)
