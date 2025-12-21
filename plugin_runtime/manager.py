from __future__ import annotations

from typing import Dict, List, Optional

from plugin_runtime.models import PluginManifest
from plugin_runtime.plugin_loader import PluginEntrypoint, discover_manifests, load_entrypoint
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

# 插件基本信息与运行入口的内存管理（单进程内有效）
_PLUGINS: Dict[str, PluginManifest] = {}
_ENTRYPOINTS: Dict[str, PluginEntrypoint] = {}
_ENABLED: Dict[str, bool] = {}


def initialize_plugins() -> None:
    """扫描并注册所有可用插件。

    - 由运行时在启动时调用；
    - 发现到的插件会写入 _PLUGINS / _ENTRYPOINTS / _ENABLED。"""

    manifests = discover_manifests()
    for manifest in manifests:
        plugin_id = manifest.plugin_id
        _PLUGINS[plugin_id] = manifest

        entrypoint = load_entrypoint(manifest)
        if entrypoint is not None:
            _ENTRYPOINTS[plugin_id] = entrypoint

        if plugin_id not in _ENABLED:
            _ENABLED[plugin_id] = True

        logger.info(
            "Plugin registered in manager",
            extra={"plugin_id": plugin_id, "entrypoint": manifest.entrypoint},
        )


def reload_plugins() -> None:
    """重新扫描插件目录并刷新内存缓存。"""

    _PLUGINS.clear()
    _ENTRYPOINTS.clear()
    # 保留 _ENABLED，避免每次刷新都丢失启用状态
    initialize_plugins()


def list_manifests() -> List[PluginManifest]:
    """返回当前所有已注册插件的 manifest 列表。"""

    return list(_PLUGINS.values())


def get_manifest(plugin_id: str) -> Optional[PluginManifest]:
    """根据 plugin_id 获取 manifest。"""

    return _PLUGINS.get(plugin_id)


def get_entrypoint(plugin_id: str) -> Optional[PluginEntrypoint]:
    """根据 plugin_id 获取入口函数。"""

    return _ENTRYPOINTS.get(plugin_id)


def register_entrypoint(plugin_id: str, entrypoint: PluginEntrypoint) -> None:
    """在运行时手动注册入口函数（用于惰性加载补偿）。"""

    _ENTRYPOINTS[plugin_id] = entrypoint


def is_enabled(plugin_id: str) -> bool:
    """当前插件是否处于启用状态。"""

    return _ENABLED.get(plugin_id, True)


def enable_plugin(plugin_id: str) -> None:
    """启用插件（仅影响 Plugin Store 展示，不影响底层加载状态）。"""

    if plugin_id not in _PLUGINS:
        logger.warning("Attempt to enable unknown plugin", extra={"plugin_id": plugin_id})
        return

    _ENABLED[plugin_id] = True


def disable_plugin(plugin_id: str) -> None:
    """禁用插件（Plugin Store 不再展示，不影响底层加载状态）。"""

    if plugin_id not in _PLUGINS:
        logger.warning("Attempt to disable unknown plugin", extra={"plugin_id": plugin_id})
        return

    _ENABLED[plugin_id] = False
