"""
结构化数据库模块

使用SQLAlchemy实现关系数据存储，提供API查询支持
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


Base = declarative_base()


class MonitoredProject(Base):
    """监控项目表"""
    __tablename__ = 'monitored_projects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    english_name = Column(String(255))
    category = Column(String(100))
    type = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    trials = relationship("ClinicalTrial", back_populates="project")
    applications = relationship("ApplicationProgress", back_populates="project")


class ClinicalTrial(Base):
    """临床试验表"""
    __tablename__ = 'clinical_trials'

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_data_id = Column(String(100), unique=True, index=True)
    project_id = Column(Integer, ForeignKey('monitored_projects.id'), index=True)

    # 核心字段
    nct_id = Column(String(50), index=True)
    title = Column(Text)
    company = Column(String(255), index=True)
    phase = Column(String(50))
    status = Column(String(100), index=True)
    indication = Column(Text)

    # 时间字段
    start_date = Column(Date)
    completion_date = Column(Date)
    primary_completion_date = Column(Date)

    # 其他
    enrollment = Column(Integer)
    source = Column(String(50))
    url = Column(Text)

    collected_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    project = relationship("MonitoredProject", back_populates="trials")


class ApplicationProgress(Base):
    """申报进度表"""
    __tablename__ = 'application_progress'

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_data_id = Column(String(100), unique=True, index=True)
    project_id = Column(Integer, ForeignKey('monitored_projects.id'), index=True)

    # 核心字段
    application_number = Column(String(100), index=True)  # 受理号
    type = Column(String(20), index=True)  # IND/NDA/ANDA
    status = Column(String(100), index=True)
    queue_number = Column(String(50))  # 排队序列号

    # 企业信息
    company = Column(String(255))
    drug_name = Column(String(255))

    # 时间
    submission_date = Column(Date)
    approval_date = Column(Date)

    # 其他
    source = Column(String(50))
    url = Column(Text)

    collected_at = Column(DateTime, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    project = relationship("MonitoredProject", back_populates="applications")


class DataChange(Base):
    """数据变更记录表（用于告警）"""
    __tablename__ = 'data_changes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('monitored_projects.id'), index=True)
    change_type = Column(String(50), index=True)  # status_change/new_item/update
    entity_type = Column(String(50))  # trial/application
    entity_id = Column(String(100))
    old_value = Column(Text)  # JSON格式
    new_value = Column(Text)  # JSON格式
    description = Column(Text)
    detected_at = Column(DateTime, default=datetime.now, index=True)

    # 关系
    project = relationship("MonitoredProject")


class StructuredDB:
    """结构化数据库管理器"""

    def __init__(self, db_url: str = "sqlite:///data/intelligence.db"):
        """
        初始化数据库连接

        Args:
            db_url: 数据库URL（默认使用SQLite）
        """
        # 确保data目录存在
        db_path = Path(db_url.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def close(self):
        """关闭数据库连接"""
        self.session.close()

    def add_project(self, name: str, english_name: str = None,
                   category: str = None, type: str = None) -> MonitoredProject:
        """
        添加监控项目

        Args:
            name: 项目名称
            english_name: 英文名称
            category: 分类
            type: 类型

        Returns:
            MonitoredProject对象
        """
        project = self.session.query(MonitoredProject).filter_by(name=name).first()

        if not project:
            project = MonitoredProject(
                name=name,
                english_name=english_name,
                category=category,
                type=type
            )
            self.session.add(project)
            self.session.commit()
            print(f"Added project: {name}")
        else:
            # 更新现有项目
            if english_name:
                project.english_name = english_name
            if category:
                project.category = category
            if type:
                project.type = type
            project.updated_at = datetime.now()
            self.session.commit()
            print(f"Updated project: {name}")

        return project

    def get_project(self, name: str) -> Optional[MonitoredProject]:
        """
        获取项目

        Args:
            name: 项目名称

        Returns:
            MonitoredProject对象或None
        """
        return self.session.query(MonitoredProject).filter_by(name=name).first()

    def save_trial(self, raw_data_id: str, extracted_data: Dict, project_name: str) -> int:
        """
        保存临床试验数据

        Args:
            raw_data_id: 原始数据ID
            extracted_data: 提取的数据字典
            project_name: 项目名称

        Returns:
            试验记录ID
        """
        # 获取或创建项目
        project = self.get_project(project_name)
        if not project:
            project = self.add_project(project_name)

        # 检查是否已存在
        trial = self.session.query(ClinicalTrial).filter_by(
            raw_data_id=raw_data_id
        ).first()

        if trial:
            # 更新 - 只更新模型中存在的字段
            valid_fields = {
                'nct_id', 'title', 'company', 'phase', 'status',
                'indication', 'start_date', 'completion_date',
                'primary_completion_date', 'enrollment', 'source', 'url'
            }

            for key, value in extracted_data.items():
                if key in valid_fields and hasattr(trial, key):
                    setattr(trial, key, value)
            trial.updated_at = datetime.now()
        else:
            # 新增 - 只传递模型中存在的字段
            trial_data = {
                'raw_data_id': raw_data_id,
                'project_id': project.id,
            }

            # 只添加ClinicalTrial模型中存在的字段
            valid_fields = {
                'nct_id', 'title', 'company', 'phase', 'status',
                'indication', 'start_date', 'completion_date',
                'primary_completion_date', 'enrollment', 'source', 'url'
            }

            for key, value in extracted_data.items():
                if key in valid_fields:
                    trial_data[key] = value

            # 添加collected_at
            trial_data['collected_at'] = datetime.now()

            trial = ClinicalTrial(**trial_data)
            self.session.add(trial)

        self.session.commit()
        return trial.id

    def save_application(self, raw_data_id: str, extracted_data: Dict, project_name: str) -> int:
        """
        保存申报进度数据

        Args:
            raw_data_id: 原始数据ID
            extracted_data: 提取的数据字典
            project_name: 项目名称

        Returns:
            申报记录ID
        """
        # 获取或创建项目
        project = self.get_project(project_name)
        if not project:
            project = self.add_project(project_name)

        # 检查是否已存在
        application = self.session.query(ApplicationProgress).filter_by(
            raw_data_id=raw_data_id
        ).first()

        if application:
            # 更新
            for key, value in extracted_data.items():
                if hasattr(application, key):
                    setattr(application, key, value)
            application.updated_at = datetime.now()
        else:
            # 新增
            application = ApplicationProgress(
                raw_data_id=raw_data_id,
                project_id=project.id,
                **extracted_data
            )
            self.session.add(application)

        self.session.commit()
        return application.id

    def get_project_trials(self, project_name: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        """
        获取项目的临床试验列表

        Args:
            project_name: 项目名称
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            试验字典列表
        """
        project = self.get_project(project_name)
        if not project:
            return []

        trials = self.session.query(ClinicalTrial).filter_by(
            project_id=project.id
        ).order_by(
            ClinicalTrial.collected_at.desc()
        ).limit(limit).offset(offset).all()

        return [
            {
                "id": t.id,
                "nct_id": t.nct_id,
                "title": t.title,
                "company": t.company,
                "phase": t.phase,
                "status": t.status,
                "indication": t.indication,
                "start_date": t.start_date.isoformat() if t.start_date else None,
                "completion_date": t.completion_date.isoformat() if t.completion_date else None,
                "enrollment": t.enrollment,
                "source": t.source,
                "collected_at": t.collected_at.isoformat() if t.collected_at else None
            }
            for t in trials
        ]

    def get_project_applications(self, project_name: str, app_type: str = None,
                               limit: int = 20, offset: int = 0) -> List[Dict]:
        """
        获取项目的申报进度列表

        Args:
            project_name: 项目名称
            app_type: 申请类型（IND/NDA/ANDA）
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            申报字典列表
        """
        project = self.get_project(project_name)
        if not project:
            return []

        query = self.session.query(ApplicationProgress).filter_by(
            project_id=project.id
        )

        if app_type:
            query = query.filter(ApplicationProgress.type == app_type.upper())

        applications = query.order_by(
            ApplicationProgress.collected_at.desc()
        ).limit(limit).offset(offset).all()

        return [
            {
                "id": a.id,
                "application_number": a.application_number,
                "type": a.type,
                "status": a.status,
                "queue_number": a.queue_number,
                "company": a.company,
                "drug_name": a.drug_name,
                "submission_date": a.submission_date.isoformat() if a.submission_date else None,
                "approval_date": a.approval_date.isoformat() if a.approval_date else None,
                "source": a.source,
                "collected_at": a.collected_at.isoformat() if a.collected_at else None
            }
            for a in applications
        ]

    def get_all_projects(self) -> List[Dict]:
        """
        获取所有监控项目

        Returns:
            项目字典列表
        """
        projects = self.session.query(MonitoredProject).all()

        return [
            {
                "id": p.id,
                "name": p.name,
                "english_name": p.english_name,
                "category": p.category,
                "type": p.type,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None
            }
            for p in projects
        ]
