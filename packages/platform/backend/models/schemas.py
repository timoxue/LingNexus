"""
Pydantic 模型：用于请求和响应的数据验证
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ==================== 基础响应模型 ====================

class ResponseModel(BaseModel):
    """通用响应模型"""
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None


# ==================== 认证相关 ====================

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """用户注册"""
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class UserResponse(UserBase):
    """用户响应"""
    id: int
    is_active: bool
    is_superuser: bool
    department: Optional[str] = None
    role: str = "user"
    xp: int = 0
    level: int = 1
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token 数据"""
    user_id: Optional[int] = None
    username: Optional[str] = None


# ==================== 技能相关 ====================

class SkillBase(BaseModel):
    """技能基础模型"""
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., pattern="^(external|internal)$")
    content: str
    meta: Optional[dict] = None


class SkillCreate(SkillBase):
    """创建技能"""
    pass


class SkillUpdate(BaseModel):
    """更新技能"""
    content: Optional[str] = None
    meta: Optional[dict] = None
    is_active: Optional[bool] = None


class SkillResponse(SkillBase):
    """技能响应"""
    id: int
    is_active: bool
    version: str
    created_by: int
    created_at: datetime
    updated_at: datetime
    sharing_scope: str = "private"
    department: Optional[str] = None
    is_official: bool = False
    usage_count: int = 0
    rating: Optional[float] = None
    rating_count: int = 0
    documentation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SkillUpdate(BaseModel):
    """更新技能"""
    content: Optional[str] = None
    meta: Optional[dict] = None
    is_active: Optional[bool] = None
    sharing_scope: Optional[str] = None
    department: Optional[str] = None
    is_official: Optional[bool] = None
    documentation: Optional[str] = None


class SkillMarketResponse(SkillResponse):
    """技能市场响应（包含额外字段）"""
    creator_name: Optional[str] = None
    is_saved: bool = False
    user_rating: Optional[int] = None


class TrySkillRequest(BaseModel):
    """试用技能请求"""
    message: str = Field(..., min_length=1)


class TrySkillResponse(BaseModel):
    """试用技能响应"""
    status: str
    output_message: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class CreateAgentFromSkillRequest(BaseModel):
    """从技能创建代理请求"""
    agent_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    model_name: str = Field(default="qwen-max")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, gt=0)


class RateSkillRequest(BaseModel):
    """评分请求"""
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)


class RatingResponse(BaseModel):
    """评分响应"""
    id: int
    user_id: int
    skill_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== 代理相关 ====================

class AgentBase(BaseModel):
    """代理基础模型"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    model_name: str = Field(..., pattern="^(qwen|max|plus|turbo|deepseek|chat|coder)(-[\\w]+)?$")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, gt=0)
    system_prompt: Optional[str] = None


class AgentCreate(AgentBase):
    """创建代理"""
    skill_ids: Optional[List[int]] = []  # 关联的技能 ID 列表


class AgentUpdate(BaseModel):
    """更新代理"""
    name: Optional[str] = None
    description: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    is_active: Optional[bool] = None
    skill_ids: Optional[List[int]] = None


class AgentResponse(AgentBase):
    """代理响应"""
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    skills: List["AgentSkillInfo"] = []

    model_config = ConfigDict(from_attributes=True)


class AgentSkillInfo(BaseModel):
    """Agent 关联技能的简化信息"""
    id: int
    name: str
    category: str


class AgentExecute(BaseModel):
    """执行代理请求"""
    message: str = Field(..., min_length=1)


class AgentExecuteResponse(BaseModel):
    """代理执行响应"""
    execution_id: int
    status: str
    output_message: Optional[str] = None
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    execution_time: Optional[float] = None
    artifacts: Optional[List[Dict[str, Any]]] = []  # Agent 生成的文件列表


# ==================== 代理执行相关 ====================

class ExecutionResponse(BaseModel):
    """执行记录响应"""
    id: int
    agent_id: int
    input_message: str
    output_message: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    execution_time: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ==================== 监控项目相关 ====================

class MonitoringProjectBase(BaseModel):
    """监控项目基础模型"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    keywords: List[str] = Field(..., min_length=1)
    companies: Optional[List[str]] = None
    indications: Optional[List[str]] = None


class MonitoringProjectCreate(MonitoringProjectBase):
    """创建监控项目"""
    pass


class MonitoringProjectUpdate(BaseModel):
    """更新监控项目"""
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    companies: Optional[List[str]] = None
    indications: Optional[List[str]] = None
    is_active: Optional[bool] = None


class MonitoringProjectResponse(MonitoringProjectBase):
    """监控项目响应"""
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime
    trial_count: int = 0  # 关联的试验数量

    model_config = ConfigDict(from_attributes=True)


# ==================== 临床试验相关 ====================

class ClinicalTrialBase(BaseModel):
    """临床试验基础模型"""
    source: str
    nct_id: Optional[str] = None
    registration_number: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None
    phase: Optional[str] = None
    company: Optional[str] = None
    indication: Optional[str] = None
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    url: Optional[str] = None


class ClinicalTrialResponse(ClinicalTrialBase):
    """临床试验响应"""
    id: int
    project_id: int
    scraped_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClinicalTrialListParams(BaseModel):
    """临床试验查询参数"""
    project_id: Optional[int] = None
    source: Optional[str] = None
    status: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# ==================== 文件管理相关 ====================

class AgentArtifactBase(BaseModel):
    """Agent 生成文件基础模型"""
    filename: str
    original_filename: Optional[str] = None
    file_type: str
    file_size: int
    mime_type: str
    category: str = "document"
    description: Optional[str] = None


class AgentArtifactCreate(AgentArtifactBase):
    """创建 Agent 生成文件"""
    agent_execution_id: int
    skill_id: Optional[int] = None
    storage_path: str
    file_id: str


class AgentArtifactResponse(AgentArtifactBase):
    """Agent 生成文件响应"""
    id: int
    file_id: str
    agent_execution_id: int
    skill_id: Optional[int] = None
    storage_path: str
    access_count: int
    last_accessed_at: Optional[datetime] = None
    created_at: datetime

    # 下载和预览 URL
    download_url: Optional[str] = None
    preview_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserFileBase(BaseModel):
    """用户文件基础模型"""
    filename: str
    file_type: str
    file_size: int
    mime_type: str
    description: Optional[str] = None
    tags: Optional[str] = None


class UserFileCreate(UserFileBase):
    """创建用户文件"""
    folder_id: Optional[int] = None
    storage_path: str
    file_id: str


class UserFileUpdate(BaseModel):
    """更新用户文件"""
    filename: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    folder_id: Optional[int] = None


class UserFileResponse(UserFileBase):
    """用户文件响应"""
    id: int
    file_id: str
    user_id: int
    folder_id: Optional[int] = None
    storage_path: str
    access_count: int
    last_accessed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # 下载和预览 URL
    download_url: Optional[str] = None
    preview_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserFolderBase(BaseModel):
    """用户文件夹基础模型"""
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    order: int = 0


class UserFolderCreate(UserFolderBase):
    """创建用户文件夹"""
    path: str


class UserFolderUpdate(BaseModel):
    """更新用户文件夹"""
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    order: Optional[int] = None


class UserFolderResponse(UserFolderBase):
    """用户文件夹响应"""
    id: int
    user_id: int
    path: str
    created_at: datetime
    updated_at: datetime

    # 文件和子文件夹数量
    file_count: int = 0
    folder_count: int = 0


# ==================== Skill Creator 相关 ====================

class AliasParameter(BaseModel):
    """别名参数定义"""
    name: str
    type: str = Field(..., pattern="^(string|number|boolean|array)$")
    required: bool = True
    description: str
    default: Optional[Any] = None
    enum: Optional[List[str]] = None



