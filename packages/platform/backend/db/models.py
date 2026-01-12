"""
数据库模型定义
"""
import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    Text,
    Boolean,
    DateTime,
    DECIMAL,
    JSON,
    ForeignKey,
    Enum,
    Index,
    Date,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """所有模型的基类"""
    pass


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # Marketplace and Team fields
    department: Mapped[Optional[str]] = mapped_column(String(100))  # 部门
    role: Mapped[str] = mapped_column(String(20), default="user")  # user/admin/super_admin
    xp: Mapped[int] = mapped_column(Integer, default=0)  # 经验值
    level: Mapped[int] = mapped_column(Integer, default=1)  # 等级

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # 关系
    skills: Mapped[list["Skill"]] = relationship(
        "Skill", back_populates="creator", cascade="all, delete-orphan"
    )
    agents: Mapped[list["Agent"]] = relationship(
        "Agent", back_populates="creator", cascade="all, delete-orphan"
    )
    monitoring_projects: Mapped[list["MonitoringProject"]] = relationship(
        "MonitoringProject", back_populates="creator", cascade="all, delete-orphan"
    )
    saved_skills: Mapped[list["SavedSkill"]] = relationship(
        "SavedSkill", back_populates="user", cascade="all, delete-orphan"
    )
    skill_ratings: Mapped[list["SkillRating"]] = relationship(
        "SkillRating", back_populates="user", cascade="all, delete-orphan"
    )


class Skill(Base):
    """技能表"""
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(20), nullable=False)  # external/internal
    content: Mapped[str] = mapped_column(Text, nullable=False)  # SKILL.md 内容
    meta: Mapped[Optional[dict]] = mapped_column(JSON)  # YAML front matter
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    # Marketplace fields
    sharing_scope: Mapped[str] = mapped_column(String(20), default="private")  # private/team/public
    department: Mapped[Optional[str]] = mapped_column(String(100))  # 所属部门
    is_official: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否官方认证
    usage_count: Mapped[int] = mapped_column(Integer, default=0)  # 使用次数
    rating: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2))  # 平均评分
    rating_count: Mapped[int] = mapped_column(Integer, default=0)  # 评分人数
    documentation: Mapped[Optional[str]] = mapped_column(Text)  # 使用文档

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # 关系
    creator: Mapped["User"] = relationship("User", back_populates="skills")
    agent_skills: Mapped[list["AgentSkill"]] = relationship(
        "AgentSkill", back_populates="skill", cascade="all, delete-orphan"
    )
    saved_by: Mapped[list["SavedSkill"]] = relationship(
        "SavedSkill", back_populates="skill", cascade="all, delete-orphan"
    )
    ratings: Mapped[list["SkillRating"]] = relationship(
        "SkillRating", back_populates="skill", cascade="all, delete-orphan"
    )

    # 索引
    __table_args__ = (
        Index("idx_sharing_scope", "sharing_scope"),
        Index("idx_category_sharing", "category", "sharing_scope"),
        Index("idx_rating", "rating"),
        Index("idx_usage", "usage_count"),
    )


class Agent(Base):
    """代理表"""
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)  # qwen-max, deepseek-chat
    temperature: Mapped[Decimal] = mapped_column(DECIMAL(3, 2), default=0.7)
    max_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    system_prompt: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # 关系
    creator: Mapped["User"] = relationship("User", back_populates="agents")
    agent_skills: Mapped[list["AgentSkill"]] = relationship(
        "AgentSkill", back_populates="agent", cascade="all, delete-orphan"
    )
    executions: Mapped[list["AgentExecution"]] = relationship(
        "AgentExecution", back_populates="agent", cascade="all, delete-orphan"
    )


class AgentSkill(Base):
    """代理-技能关联表"""
    __tablename__ = "agent_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    agent_id: Mapped[int] = mapped_column(Integer, ForeignKey("agents.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id"), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # 关系
    agent: Mapped["Agent"] = relationship("Agent", back_populates="agent_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="agent_skills")

    # 唯一约束：同一个 agent 和 skill 的组合只能有一条记录
    __table_args__ = (Index("idx_agent_skill", "agent_id", "skill_id", unique=True),)


class AgentExecution(Base):
    """代理执行记录表"""
    __tablename__ = "agent_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    agent_id: Mapped[int] = mapped_column(Integer, ForeignKey("agents.id"), nullable=False)
    input_message: Mapped[str] = mapped_column(Text, nullable=False)
    output_message: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        Enum("pending", "running", "success", "failed", name="execution_status"),
        default="pending",
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    execution_time: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 3))  # 秒
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    # 关系
    agent: Mapped["Agent"] = relationship("Agent", back_populates="executions")
    execution_skills: Mapped[list["AgentExecutionSkill"]] = relationship(
        "AgentExecutionSkill", back_populates="execution", cascade="all, delete-orphan"
    )

    # 索引
    __table_args__ = (
        Index("idx_agent_status", "agent_id", "status"),
        Index("idx_created_at", "created_at"),
    )


class AgentExecutionSkill(Base):
    """代理执行时使用的技能记录表"""
    __tablename__ = "agent_execution_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    agent_execution_id: Mapped[int] = mapped_column(Integer, ForeignKey("agent_executions.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id"), nullable=False)
    tool_calls: Mapped[Optional[dict]] = mapped_column(JSON)  # 记录调用了哪些工具 {tool_name: call_count}
    success: Mapped[bool] = mapped_column(Boolean, default=True)  # 该skill的调用是否成功
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # 关系
    execution: Mapped["AgentExecution"] = relationship("AgentExecution", back_populates="execution_skills")
    skill: Mapped["Skill"] = relationship("Skill")

    # 唯一约束：同一个execution和skill的组合只能有一条记录
    __table_args__ = (Index("idx_execution_skill", "agent_execution_id", "skill_id", unique=True),)


class MonitoringProject(Base):
    """监控项目表"""
    __tablename__ = "monitoring_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    keywords: Mapped[list] = mapped_column(JSON, nullable=False)  # 关键词列表
    companies: Mapped[Optional[list]] = mapped_column(JSON)  # 竞争企业
    indications: Mapped[Optional[list]] = mapped_column(JSON)  # 适应症
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # 关系
    creator: Mapped["User"] = relationship("User", back_populates="monitoring_projects")
    clinical_trials: Mapped[list["ClinicalTrial"]] = relationship(
        "ClinicalTrial", back_populates="project", cascade="all, delete-orphan"
    )


class ClinicalTrial(Base):
    """临床试验数据表"""
    __tablename__ = "clinical_trials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("monitoring_projects.id"), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # clinicaltrials, cde, insight
    nct_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)  # ClinicalTrials.gov ID
    registration_number: Mapped[Optional[str]] = mapped_column(String(100))  # CDE 注册号
    title: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    phase: Mapped[Optional[str]] = mapped_column(String(50))
    company: Mapped[Optional[str]] = mapped_column(String(200))  # 申办方/企业
    indication: Mapped[Optional[str]] = mapped_column(Text)  # 适应症
    start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    completion_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    url: Mapped[Optional[str]] = mapped_column(Text)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON)  # 原始数据
    scraped_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # 关系
    project: Mapped["MonitoringProject"] = relationship("MonitoringProject", back_populates="clinical_trials")

    # 索引
    __table_args__ = (
        Index("idx_project_source", "project_id", "source"),
        Index("idx_nct_id", "nct_id"),
        Index("idx_scraped_at", "scraped_at"),
    )


class SavedSkill(Base):
    """用户收藏的技能表"""
    __tablename__ = "saved_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="saved_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="saved_by")

    # 唯一约束：同一个 user 和 skill 的组合只能有一条记录
    __table_args__ = (Index("idx_user_skill", "user_id", "skill_id", unique=True),)


class SkillRating(Base):
    """技能评分表"""
    __tablename__ = "skill_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5 分
    comment: Mapped[Optional[str]] = mapped_column(Text)  # 评论文本
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="skill_ratings")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="ratings")

    # 唯一约束：同一个 user 和 skill 的组合只能有一条评分记录
    __table_args__ = (Index("idx_user_skill_rating", "user_id", "skill_id", unique=True),)
