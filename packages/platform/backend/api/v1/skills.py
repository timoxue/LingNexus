"""
技能管理 API 端点
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from db.models import User, Skill
from core.deps import get_current_active_user
from models.schemas import SkillCreate, SkillUpdate, SkillResponse

router = APIRouter(prefix="/skills", tags=["Skills"])


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
