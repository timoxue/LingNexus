from typing import List, Optional

from pydantic import BaseModel, Field


class RDRequest(BaseModel):
    """药物研发请求模型（骨架）。"""

    compound: str = Field(..., description="化合物名称或 SMILES")
    context: Optional[str] = Field(None, description="额外上下文")


class RDResponse(BaseModel):
    """药物研发响应模型（骨架）。"""

    summary: str = Field(..., description="研发分析总结")
    predictions: List[str] = Field(default_factory=list, description="预测结果")
