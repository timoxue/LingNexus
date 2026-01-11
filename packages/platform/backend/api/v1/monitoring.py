"""
监控数据 API 端点
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.session import get_db
from db.models import User, MonitoringProject, ClinicalTrial
from core.deps import get_current_active_user
from models.schemas import (
    MonitoringProjectCreate,
    MonitoringProjectUpdate,
    MonitoringProjectResponse,
    ClinicalTrialResponse,
    ClinicalTrialListParams,
)

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


# ==================== 监控项目 ====================

@router.get("/projects", response_model=List[MonitoringProjectResponse])
async def list_monitoring_projects(
    is_active: bool = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db),
) -> Any:
    """
    获取监控项目列表

    Args:
        is_active: 是否活跃过滤
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话

    Returns:
        List[MonitoringProjectResponse]: 监控项目列表
    """
    query = db.query(MonitoringProject)

    # 应用过滤条件
    if is_active is not None:
        query = query.filter(MonitoringProject.is_active == is_active)

    # 分页
    projects = query.order_by(MonitoringProject.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for project in projects:
        # 统计关联的试验数量
        trial_count = db.query(ClinicalTrial).filter(
            ClinicalTrial.project_id == project.id
        ).count()

        project_dict = MonitoringProjectResponse.model_validate(project).model_dump()
        project_dict["trial_count"] = trial_count
        result.append(MonitoringProjectResponse(**project_dict))

    return result


@router.get("/projects/{project_id}", response_model=MonitoringProjectResponse)
async def get_monitoring_project(
    project_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    获取单个监控项目详情

    Args:
        project_id: 项目 ID
        db: 数据库会话

    Returns:
        MonitoringProjectResponse: 项目详情

    Raises:
        HTTPException: 项目不存在
    """
    project = db.query(MonitoringProject).filter(MonitoringProject.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring project not found",
        )

    # 统计关联的试验数量
    trial_count = db.query(ClinicalTrial).filter(
        ClinicalTrial.project_id == project.id
    ).count()

    project_dict = MonitoringProjectResponse.model_validate(project).model_dump()
    project_dict["trial_count"] = trial_count

    return MonitoringProjectResponse(**project_dict)


@router.post("/projects", response_model=MonitoringProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_monitoring_project(
    project_in: MonitoringProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新监控项目

    Args:
        project_in: 项目创建信息
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        MonitoringProjectResponse: 创建的项目
    """
    # 检查项目名是否已存在
    existing_project = db.query(MonitoringProject).filter(
        MonitoringProject.name == project_in.name
    ).first()
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project name already exists",
        )

    # 创建项目
    project = MonitoringProject(
        name=project_in.name,
        description=project_in.description,
        keywords=project_in.keywords,
        companies=project_in.companies,
        indications=project_in.indications,
        created_by=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return MonitoringProjectResponse.model_validate(project)


@router.put("/projects/{project_id}", response_model=MonitoringProjectResponse)
async def update_monitoring_project(
    project_id: int,
    project_in: MonitoringProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新监控项目

    Args:
        project_id: 项目 ID
        project_in: 项目更新信息
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        MonitoringProjectResponse: 更新后的项目

    Raises:
        HTTPException: 项目不存在或无权限
    """
    project = db.query(MonitoringProject).filter(MonitoringProject.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring project not found",
        )

    # 检查权限（只有创建者可以修改）
    if project.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # 更新字段
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    return MonitoringProjectResponse.model_validate(project)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_monitoring_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    删除监控项目

    Args:
        project_id: 项目 ID
        db: 数据库会话
        current_user: 当前登录用户

    Raises:
        HTTPException: 项目不存在或无权限
    """
    project = db.query(MonitoringProject).filter(MonitoringProject.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitoring project not found",
        )

    # 检查权限（只有创建者可以删除）
    if project.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    db.delete(project)
    db.commit()


# ==================== 临床试验数据 ====================

@router.get("/trials", response_model=list[ClinicalTrialResponse])
async def list_clinical_trials(
    project_id: int = Query(None, description="Filter by project ID"),
    source: str = Query(None, description="Filter by data source"),
    status: str = Query(None, description="Filter by trial status"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
) -> Any:
    """
    获取临床试验数据列表

    Args:
        project_id: 项目 ID 过滤
        source: 数据源过滤 (clinicaltrials, cde, insight)
        status: 试验状态过滤
        limit: 返回记录数
        offset: 跳过记录数
        db: 数据库会话

    Returns:
        List[ClinicalTrialResponse]: 临床试验数据列表
    """
    query = db.query(ClinicalTrial)

    # 应用过滤条件
    if project_id is not None:
        query = query.filter(ClinicalTrial.project_id == project_id)
    if source:
        query = query.filter(ClinicalTrial.source == source)
    if status:
        query = query.filter(ClinicalTrial.status == status)

    # 分页
    trials = query.order_by(ClinicalTrial.scraped_at.desc()).offset(offset).limit(limit).all()

    return [ClinicalTrialResponse.model_validate(trial) for trial in trials]


@router.get("/trials/{trial_id}", response_model=ClinicalTrialResponse)
async def get_clinical_trial(
    trial_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    获取单个临床试验详情

    Args:
        trial_id: 试验 ID
        db: 数据库会话

    Returns:
        ClinicalTrialResponse: 试验详情

    Raises:
        HTTPException: 试验不存在
    """
    trial = db.query(ClinicalTrial).filter(ClinicalTrial.id == trial_id).first()

    if not trial:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical trial not found",
        )

    return ClinicalTrialResponse.model_validate(trial)


@router.get("/statistics")
async def get_monitoring_statistics(
    db: Session = Depends(get_db),
) -> Any:
    """
    获取监控统计信息

    Args:
        db: 数据库会话

    Returns:
        dict: 统计信息
    """
    # 统计项目数量
    total_projects = db.query(MonitoringProject).count()
    active_projects = db.query(MonitoringProject).filter(
        MonitoringProject.is_active == True
    ).count()

    # 统计试验数量
    total_trials = db.query(ClinicalTrial).count()

    # 按数据源统计
    source_stats = db.query(
        ClinicalTrial.source,
        func.count(ClinicalTrial.id)
    ).group_by(ClinicalTrial.source).all()

    source_counts = {source: count for source, count in source_stats}

    # 按状态统计
    status_stats = db.query(
        ClinicalTrial.status,
        func.count(ClinicalTrial.id)
    ).group_by(ClinicalTrial.status).all()

    status_counts = {status: count for status, count in status_stats}

    return {
        "projects": {
            "total": total_projects,
            "active": active_projects,
        },
        "trials": {
            "total": total_trials,
            "by_source": source_counts,
            "by_status": status_counts,
        },
    }
