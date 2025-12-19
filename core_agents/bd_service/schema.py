from typing import List, Optional

from pydantic import BaseModel, Field


class BDRequest(BaseModel):
    """BD 流程请求模型（骨架）。"""

    target: str = Field(..., description="目标企业或项目")
    context: Optional[str] = Field(None, description="额外上下文")


class BDResponse(BaseModel):
    """BD 流程响应模型（骨架）。"""

    summary: str = Field(..., description="BD 分析总结")
    recommendations: List[str] = Field(default_factory=list, description="推荐操作")
