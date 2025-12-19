from typing import List, Optional

from pydantic import BaseModel, Field


class IntelligenceRequest(BaseModel):
    """情报分析请求模型。"""

    query: str = Field(..., description="用户查询（如项目名称、药物名称等）")
    context: Optional[str] = Field(None, description="额外业务上下文信息")
    top_k: int = Field(5, description="检索结果数量上限")


class IntelligenceSource(BaseModel):
    """情报来源信息。"""

    title: str
    url: Optional[str] = None
    source_type: Optional[str] = Field(None, description="来源类型，如 clinical_trial/patent/report")


class IntelligenceResponse(BaseModel):
    """情报分析响应模型。"""

    summary: str = Field(..., description="情报总结")
    key_points: List[str] = Field(default_factory=list, description="关键要点")
    sources: List[IntelligenceSource] = Field(default_factory=list, description="引用来源列表")
