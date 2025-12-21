from __future__ import annotations

import os
from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from shared.utils.logging_utils import get_logger, setup_logging

# 初始化日志
setup_logging()
logger = get_logger(__name__)

# Plugin Store Backend 本身的 FastAPI 应用
app = FastAPI(
    title="LingNexus Plugin Store Backend",
    description="内部插件应用商店后端（通过 plugin_runtime 运行插件）",
    version="0.1.0",
)

# plugin_runtime 服务的基础 URL，可通过环境变量覆盖
PLUGIN_RUNTIME_BASE_URL = os.getenv("PLUGIN_RUNTIME_URL", "http://127.0.0.1:8015")


class RunPluginRequest(BaseModel):
    """从前端运行插件时的请求结构。

    此处对 payload 不做强约束，交由前端和 plugin_manifest 协同约束。
    """

    payload: Dict[str, Any] = Field(default_factory=dict)


@app.get("/api/plugins")
async def list_plugins() -> Any:
    """Plugin Store 插件列表视图。

    直接透传 plugin_runtime 的 `/store/plugins` 输出，前端可按需裁剪展示字段。
    """

    url = f"{PLUGIN_RUNTIME_BASE_URL}/store/plugins"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
        resp.raise_for_status()
    except httpx.HTTPError as exc:  # noqa: BLE001
        logger.error("Failed to list plugins from runtime", extra={"error": str(exc)})
        raise HTTPException(status_code=502, detail="Plugin runtime unavailable") from exc

    return resp.json()


@app.get("/api/plugins/{plugin_id}")
async def get_plugin_detail(plugin_id: str) -> Any:
    """Plugin Store 插件详情视图。

    调用 plugin_runtime 的 `/plugins/{plugin_id}/detail`，用于渲染详情页和动态表单。
    """

    url = f"{PLUGIN_RUNTIME_BASE_URL}/plugins/{plugin_id}/detail"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Plugin not found")
        resp.raise_for_status()
    except httpx.HTTPError as exc:  # noqa: BLE001
        logger.error(
            "Failed to get plugin detail from runtime",
            extra={"plugin_id": plugin_id, "error": str(exc)},
        )
        raise HTTPException(status_code=502, detail="Plugin runtime unavailable") from exc

    return resp.json()


@app.post("/api/plugins/{plugin_id}/run")
async def run_plugin(plugin_id: str, req: RunPluginRequest) -> Any:
    """运行指定插件。

    - 前端提交的 payload 将转发给 plugin_runtime 的 `/plugins/{plugin_id}/invoke`；
    - 将 runtime 返回的 `PluginInvokeResponse` 原样透传给前端。
    """

    url = f"{PLUGIN_RUNTIME_BASE_URL}/plugins/{plugin_id}/invoke"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json={"payload": req.payload})
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Plugin not found")
        resp.raise_for_status()
    except httpx.HTTPError as exc:  # noqa: BLE001
        logger.error(
            "Failed to invoke plugin via runtime",
            extra={"plugin_id": plugin_id, "error": str(exc)},
        )
        raise HTTPException(status_code=502, detail="Plugin runtime unavailable") from exc

    # 返回 PluginInvokeResponse 的 JSON 结构，前端可根据 success/data/message 渲染
    return resp.json()
