from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PluginSummary(BaseModel):
    """插件列表视图，用于 Plugin Store / 前端展示。"""

    plugin_id: str
    name: str
    version: str
    category: str
    icon: Optional[str] = None
    description: Optional[str] = None


class PluginManifest(BaseModel):
    """插件 manifest 结构，对应 plugin_manifest.json。

    为了保持灵活性，这里不强行解析 input_schema/output_schema 的内部结构，
    而是按自由 dict 存储，由调用方和前端按约定解析。
    """

    plugin_id: str
    version: str
    name: str
    description: str
    author: str
    category: str
    required_skills: List[str] = Field(default_factory=list)
    entrypoint: str
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    permissions: List[str] = Field(default_factory=list)
    icon: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class PluginDetail(PluginSummary):
    """插件详细信息视图，面向 Plugin Store 详情页。"""

    author: str
    required_skills: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True  # 添加 enabled 字段


class PluginStoreItem(PluginDetail):
    """用于 Plugin Store 列表视图的插件信息，包含启用状态。"""

    enabled: bool = True


class PluginInvokeResponse(BaseModel):
    """插件执行的统一响应格式（不含 HTTP 状态）。"""

    success: bool = True
    data: Any = None
    message: str = ""
    meta: Dict[str, Any] = Field(default_factory=dict)
