from typing import Any, Dict, List

import importlib

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from plugin_runtime.models import PluginDetail, PluginInvokeResponse, PluginStoreItem, PluginSummary
from plugin_runtime.registry import get_entrypoint, get_manifest, list_manifests, load_plugins
from shared.utils.logging_utils import get_logger, setup_logging

# 插件启用状态（简易内存实现）：默认所有已加载插件均为启用状态
_ENABLED_PLUGINS: Dict[str, bool] = {}


# 初始化日志
setup_logging()
logger = get_logger(__name__)


app = FastAPI(
    title="LingNexus Plugin Runtime",
    description="插件运行时服务（MVP）",
    version="0.1.0",
)

# 应用启动时加载插件
load_plugins()


def _initialize_enabled_plugins() -> None:
    """根据已加载的插件列表初始化启用状态。

    当前实现为内存级别的开关：
    - 新加载的插件默认 enabled=True；
    - 后续可通过 /store 接口修改状态，仅在进程生命周期内生效。
    """

    for manifest in list_manifests():
        if manifest.plugin_id not in _ENABLED_PLUGINS:
            _ENABLED_PLUGINS[manifest.plugin_id] = True


_initialize_enabled_plugins()


class InvokeRequest(BaseModel):
    """运行插件时的输入包裹。

    为了保持通用性，这里直接接受任意 JSON 对象作为 payload，
    实际结构应与 plugin_manifest.json 中的 input_schema 对齐。
    """

    payload: Dict[str, Any] = Field(default_factory=dict)


@app.get("/plugins", response_model=List[PluginSummary])
async def list_plugins() -> List[PluginSummary]:
    """列出当前可用的插件列表。"""

    manifests = list_manifests()
    return [
        PluginSummary(
            plugin_id=m.plugin_id,
            name=m.name,
            version=m.version,
            category=m.category,
            icon=m.icon,
            description=m.description,
        )
        for m in manifests
    ]


@app.get("/plugins/{plugin_id}/schema")
async def get_plugin_schema(plugin_id: str) -> Dict[str, Any]:
    """获取指定插件的输入/输出 Schema（用于前端动态生成表单等）。"""

    manifest = get_manifest(plugin_id)
    if manifest is None:
        raise HTTPException(status_code=404, detail="Plugin not found")

    return {
        "plugin_id": manifest.plugin_id,
        "input_schema": manifest.input_schema,
        "output_schema": manifest.output_schema,
    }


@app.get("/store/plugins", response_model=List[PluginStoreItem])
async def list_store_plugins() -> List[PluginStoreItem]:
    """Skill Store 视角的插件列表（包含启用状态）。"""

    items: List[PluginStoreItem] = []
    for manifest in list_manifests():
        enabled = _ENABLED_PLUGINS.get(manifest.plugin_id, True)
        items.append(
            PluginStoreItem(
                plugin_id=manifest.plugin_id,
                name=manifest.name,
                version=manifest.version,
                category=manifest.category,
                icon=manifest.icon,
                description=manifest.description,
                author=manifest.author,
                required_skills=manifest.required_skills,
                permissions=manifest.permissions,
                tags=manifest.tags,
                input_schema=manifest.input_schema,
                output_schema=manifest.output_schema,
                enabled=enabled,
            )
        )
    return items


@app.get("/plugins/{plugin_id}/detail", response_model=PluginDetail)
async def get_plugin_detail(plugin_id: str) -> PluginDetail:
    """获取插件的完整配置信息，供 Skill Store 详情页使用。"""

    manifest = get_manifest(plugin_id)
    if manifest is None:
        raise HTTPException(status_code=404, detail="Plugin not found")

    enabled = _ENABLED_PLUGINS.get(plugin_id, True)

    return PluginDetail(
        plugin_id=manifest.plugin_id,
        name=manifest.name,
        version=manifest.version,
        category=manifest.category,
        icon=manifest.icon,
        description=manifest.description,
        author=manifest.author,
        required_skills=manifest.required_skills,
        permissions=manifest.permissions,
        tags=manifest.tags,
        input_schema=manifest.input_schema,
        output_schema=manifest.output_schema,
    )


@app.post("/store/plugins/{plugin_id}/enable")
async def enable_plugin(plugin_id: str) -> Dict[str, Any]:
    """启用指定插件（仅影响 Skill Store 展示，不影响底层加载）。"""

    manifest = get_manifest(plugin_id)
    if manifest is None:
        raise HTTPException(status_code=404, detail="Plugin not found")

    _ENABLED_PLUGINS[plugin_id] = True
    return {"plugin_id": plugin_id, "enabled": True}


@app.post("/store/plugins/{plugin_id}/disable")
async def disable_plugin(plugin_id: str) -> Dict[str, Any]:
    """禁用指定插件（Skill Store 不再展示，不影响底层加载）。"""

    manifest = get_manifest(plugin_id)
    if manifest is None:
        raise HTTPException(status_code=404, detail="Plugin not found")

    _ENABLED_PLUGINS[plugin_id] = False
    return {"plugin_id": plugin_id, "enabled": False}


@app.post("/plugins/{plugin_id}/invoke", response_model=PluginInvokeResponse)
async def invoke_plugin(plugin_id: str, req: InvokeRequest) -> PluginInvokeResponse:
    """执行指定插件。

    - 根据 plugin_id 查找 manifest 与入口函数；
    - 目前暂不做严格的 input_schema 校验，由调用方保证输入格式正确；
    - 捕获执行过程中的异常并返回 success=False 的响应，避免中断服务。
    """

    manifest = get_manifest(plugin_id)
    if manifest is None:
        raise HTTPException(status_code=404, detail="Plugin not found")

    entrypoint = get_entrypoint(plugin_id)
    if entrypoint is None:
        # 如果启动阶段加载失败，这里尝试惰性导入一次，避免因为一次错误导致一直不可用
        try:
            module_path, attr_name = manifest.entrypoint.split(":", 1)
            module = importlib.import_module(module_path)
            entrypoint = getattr(module, attr_name)
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Lazy import of plugin entrypoint failed",
                extra={"plugin_id": plugin_id, "entrypoint": manifest.entrypoint, "error": str(exc)},
            )
            raise HTTPException(status_code=500, detail=f"Plugin entrypoint import failed: {exc}")

    logger.info("Invoking plugin", extra={"plugin_id": plugin_id})

    try:
        result = await entrypoint(req.payload, context={"plugin_id": plugin_id})
        return PluginInvokeResponse(
            success=True,
            data=result,
            message="",
            meta={"plugin_id": plugin_id},
        )
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Plugin execution failed",
            extra={"plugin_id": plugin_id, "error": str(exc)},
        )
        return PluginInvokeResponse(
            success=False,
            data=None,
            message=str(exc),
            meta={"plugin_id": plugin_id},
        )
