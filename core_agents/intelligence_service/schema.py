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


class TopicConfig(BaseModel):
    """订阅主题配置。"""

    topic_id: str = Field(..., description="主题唯一 ID")
    name: str = Field(..., description="主题名称，例如 PD-1 肺癌")
    description: Optional[str] = Field(None, description="主题说明，给分析用的人类可读描述")
    keywords: List[str] = Field(default_factory=list, description="用于检索的关键词列表")
    max_items: int = Field(10, ge=1, le=50, description="单个主题返回的最大资讯条数")


class UserConfig(BaseModel):
    """订阅用户配置（简化版）。"""

    user_id: str = Field(..., description="用户唯一 ID")
    email: Optional[str] = Field(None, description="用户邮箱（用于后续推送）")
    subscribed_topics: List[str] = Field(default_factory=list, description="订阅的 topic_id 列表")
    role: Optional[str] = Field(
        None,
        description="用户角色，例如 bd/med/market，用于个性化订阅日报风格",
    )


class NewsItem(BaseModel):
    """医药资讯条目。"""

    id: str = Field(..., description="资讯 ID")
    title: str = Field(..., description="资讯标题")
    summary: Optional[str] = Field(None, description="简要摘要")
    source: Optional[str] = Field(None, description="来源，如 FDA/NEJM/企业新闻稿")
    category: Optional[str] = Field(None, description="分类标签")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    published_at: Optional[str] = Field(None, description="发布时间，ISO 日期或字符串")
    url: Optional[str] = Field(None, description="原文链接")
    score: Optional[float] = Field(None, description="相关性得分（可选）")


class DailyDigestItem(BaseModel):
    """单个主题的订阅日报结果。"""

    topic: TopicConfig
    news: List[NewsItem]
    digest_summary: str = Field(..., description="该主题的摘要内容，已经适合直接推送")
    role: Optional[str] = Field(
        None,
        description="该日报主要面向的用户角色，例如 bd/med/market，便于后续个性化展示",
    )


class DailyDigestRequest(BaseModel):
    """订阅日报生成请求模型（供 n8n 内部调用）。"""

    topics: List[TopicConfig] = Field(..., description="需要生成日报的主题列表")
    users: List[UserConfig] = Field(default_factory=list, description="订阅用户列表")


class DailyDigestResponse(BaseModel):
    """订阅日报生成响应模型。"""

    task_id: str = Field(..., description="本次任务 ID")
    status: str = Field("completed", description="任务状态，例如 accepted/completed/failed")
    items: List[DailyDigestItem] = Field(default_factory=list, description="各主题的日报结果列表")
