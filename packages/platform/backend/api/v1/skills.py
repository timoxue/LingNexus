"""
技能管理 API 端点
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db.session import get_db
from db.models import User, Skill
from core.deps import get_current_active_user
from models.schemas import SkillCreate, SkillUpdate, SkillResponse
from services.skill_sync import SkillSyncService, get_framework_path

router = APIRouter(prefix="/skills", tags=["Skills"])


class SkillSyncResponse(BaseModel):
    """技能同步响应"""
    total: int
    created: int
    updated: int
    skipped: int
    failed: int
    errors: List[str]
    message: str


@router.get("", response_model=List[SkillResponse])
async def list_skills(
    category: str = Query(None, description="Filter by category (external/internal)"),
    is_active: bool = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db),
) -> Any:
    """
    获取技能列表

    Args:
        category: 技能类别过滤
        is_active: 是否活跃过滤
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话

    Returns:
        List[SkillResponse]: 技能列表
    """
    query = db.query(Skill)

    # 应用过滤条件
    if category:
        query = query.filter(Skill.category == category)
    if is_active is not None:
        query = query.filter(Skill.is_active == is_active)

    # 分页
    skills = query.order_by(Skill.created_at.desc()).offset(skip).limit(limit).all()

    return [SkillResponse.model_validate(skill) for skill in skills]


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    获取单个技能详情

    Args:
        skill_id: 技能 ID
        db: 数据库会话

    Returns:
        SkillResponse: 技能详情

    Raises:
        HTTPException: 技能不存在
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    return SkillResponse.model_validate(skill)


@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_in: SkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新技能

    Args:
        skill_in: 技能创建信息
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        SkillResponse: 创建的技能
    """
    # 检查技能名是否已存在
    existing_skill = db.query(Skill).filter(Skill.name == skill_in.name).first()
    if existing_skill:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill name already exists",
        )

    # 创建技能
    skill = Skill(
        name=skill_in.name,
        category=skill_in.category,
        content=skill_in.content,
        meta=skill_in.meta,
        created_by=current_user.id,
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)

    return SkillResponse.model_validate(skill)


@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: int,
    skill_in: SkillUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新技能

    Args:
        skill_id: 技能 ID
        skill_in: 技能更新信息
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        SkillResponse: 更新后的技能

    Raises:
        HTTPException: 技能不存在或无权限
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    # 检查权限（只有创建者可以修改）
    if skill.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # 更新字段
    update_data = skill_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(skill, field, value)

    db.commit()
    db.refresh(skill)

    return SkillResponse.model_validate(skill)


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    删除技能

    Args:
        skill_id: 技能 ID
        db: 数据库会话
        current_user: 当前登录用户

    Raises:
        HTTPException: 技能不存在或无权限
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    # 检查权限（只有创建者可以删除）
    if skill.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    db.delete(skill)
    db.commit()


@router.post("/sync", response_model=SkillSyncResponse)
async def sync_skills(
    force_update: bool = Query(False, description="是否强制更新已存在的技能"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    从 Framework 自动同步技能到 Platform 数据库

    扫描 Framework 的 skills 目录，自动导入或更新技能：
    - 扫描 skills/external/ 和 skills/internal/ 目录
    - 解析 SKILL.md 文件（包含 YAML front matter）
    - 自动创建新技能或更新已存在的技能
    - 所有同步的技能默认为公开（public）和官方（is_official=True）

    Args:
        force_update: 是否强制更新已存在的技能（默认 False）
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        SkillSyncResponse: 同步结果统计

    Example:
        POST /api/v1/skills/sync?force_update=true
    """
    # 只有管理员可以同步技能
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can sync skills"
        )

    # 获取 Framework 路径
    framework_path = get_framework_path()

    if not framework_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework path not found: {framework_path}"
        )

    # 创建同步服务
    sync_service = SkillSyncService(framework_path)

    # 执行同步
    stats = sync_service.sync_all_skills(
        db=db,
        created_by=current_user.id,
        force_update=force_update
    )

    # 构建响应消息
    message_parts = []
    if stats["created"] > 0:
        message_parts.append(f"创建 {stats['created']} 个新技能")
    if stats["updated"] > 0:
        message_parts.append(f"更新 {stats['updated']} 个技能")
    if stats["skipped"] > 0:
        message_parts.append(f"跳过 {stats['skipped']} 个已存在技能")
    if stats["failed"] > 0:
        message_parts.append(f"{stats['failed']} 个失败")

    message = "、".join(message_parts) if message_parts else "没有技能需要同步"

    return SkillSyncResponse(
        total=stats["total"],
        created=stats["created"],
        updated=stats["updated"],
        skipped=stats["skipped"],
        failed=stats["failed"],
        errors=stats["errors"],
        message=message
    )


@router.get("/sync/status", response_model=dict)
async def get_sync_status(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取技能同步状态

    返回 Framework skills 目录的状态信息，帮助了解可同步的技能数量

    Args:
        current_user: 当前登录用户

    Returns:
        dict: 同步状态信息
    """
    framework_path = get_framework_path()
    skills_dir = framework_path / "skills"

    status_info = {
        "framework_path": str(framework_path),
        "skills_dir_exists": skills_dir.exists(),
        "external_skills_count": 0,
        "internal_skills_count": 0,
        "total_skills_count": 0
    }

    if not skills_dir.exists():
        return status_info

    # 统计 external skills
    external_dir = skills_dir / "external"
    if external_dir.exists():
        status_info["external_skills_count"] = sum(
            1 for p in external_dir.iterdir()
            if p.is_dir() and (p / "SKILL.md").exists()
        )

    # 统计 internal skills
    internal_dir = skills_dir / "internal"
    if internal_dir.exists():
        status_info["internal_skills_count"] = sum(
            1 for p in internal_dir.iterdir()
            if p.is_dir() and (p / "SKILL.md").exists()
        )

    status_info["total_skills_count"] = (
        status_info["external_skills_count"] + status_info["internal_skills_count"]
    )

    return status_info
