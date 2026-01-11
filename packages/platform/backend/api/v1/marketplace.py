"""
技能市场 API 端点
"""
import time
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from db.session import get_db
from db.models import User, Skill, Agent, SavedSkill, SkillRating, AgentSkill
from core.deps import get_current_active_user, get_current_user_optional
from models.schemas import (
    SkillMarketResponse,
    TrySkillRequest,
    TrySkillResponse,
    CreateAgentFromSkillRequest,
    AgentResponse,
    RateSkillRequest,
    RatingResponse,
)

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


def _can_access_skill(skill: Skill, user: Optional[User]) -> bool:
    """
    检查用户是否有权限访问技能

    Args:
        skill: 技能对象
        user: 用户对象 (None 表示未登录)

    Returns:
        bool: 是否有权限
    """
    # 公开技能，所有人都可以访问
    if skill.sharing_scope == "public":
        return True

    # 未登录用户只能访问公开技能
    if user is None:
        return False

    # 超级管理员可以访问所有技能
    if user.is_superuser:
        return True

    # 私有技能，只有创建者可以访问
    if skill.sharing_scope == "private":
        return skill.created_by == user.id

    # 团队技能，同部门或创建者可以访问
    if skill.sharing_scope == "team":
        if skill.created_by == user.id:
            return True
        if skill.department and skill.department == user.department:
            return True
        return False

    return False


@router.get("/skills", response_model=List[SkillMarketResponse])
async def list_marketplace_skills(
    category: str = Query(None, description="Filter by category (external/internal)"),
    sharing_scope: str = Query(None, description="Filter by sharing scope (private/team/public)"),
    search: str = Query(None, description="Search in name and description"),
    sort_by: str = Query("created_at", description="Sort by field (created_at/rating/usage_count)"),
    department: str = Query(None, description="Filter by department"),
    is_official: bool = Query(None, description="Filter by official skills"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Any:
    """
    获取技能市场列表

    Args:
        category: 技能类别过滤
        sharing_scope: 共享范围过滤
        search: 搜索关键词
        sort_by: 排序字段
        department: 部门过滤
        is_official: 是否官方认证
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话
        current_user: 当前登录用户 (可选)

    Returns:
        List[SkillMarketResponse]: 技能列表
    """
    query = db.query(Skill)

    # 只显示活跃的技能
    query = query.filter(Skill.is_active == True)

    # 应用过滤条件
    if category:
        query = query.filter(Skill.category == category)

    # 权限过滤
    if current_user:
        if current_user.is_superuser:
            # 超级管理员可以看到所有技能
            if sharing_scope:
                query = query.filter(Skill.sharing_scope == sharing_scope)
        else:
            # 普通用户只能看到有权限的技能
            if sharing_scope:
                # 如果指定了 sharing_scope，还需要检查权限
                if sharing_scope == "private":
                    # 私有技能只能看到自己创建的
                    query = query.filter(
                        Skill.sharing_scope == "private",
                        Skill.created_by == current_user.id,
                    )
                elif sharing_scope == "team":
                    # 团队技能可以看到同部门的或自己创建的
                    query = query.filter(
                        Skill.sharing_scope == "team",
                        or_(
                            Skill.created_by == current_user.id,
                            Skill.department == current_user.department,
                        ),
                    )
                else:  # public
                    query = query.filter(Skill.sharing_scope == "public")
            else:
                # 没有指定 sharing_scope，显示所有有权限的
                query = query.filter(
                    or_(
                        Skill.sharing_scope == "public",
                        Skill.created_by == current_user.id,
                        Skill.department == current_user.department,
                    )
                )
    else:
        # 未登录用户只能看到公开技能
        query = query.filter(Skill.sharing_scope == "public")
        if sharing_scope and sharing_scope != "public":
            # 未登录用户请求非公开技能，返回空
            return []

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Skill.name.ilike(search_pattern),
                Skill.content.ilike(search_pattern),
            )
        )

    if department:
        query = query.filter(Skill.department == department)

    if is_official is not None:
        query = query.filter(Skill.is_official == is_official)

    # 排序
    if sort_by == "rating":
        query = query.order_by(Skill.rating.desc(), Skill.created_at.desc())
    elif sort_by == "usage_count":
        query = query.order_by(Skill.usage_count.desc(), Skill.created_at.desc())
    else:  # created_at
        query = query.order_by(Skill.created_at.desc())

    # 分页
    skills = query.offset(skip).limit(limit).all()

    # 构建响应
    result = []
    for skill in skills:
        skill_dict = SkillMarketResponse.model_validate(skill).model_dump()

        # 添加创建者名称
        creator = db.query(User).filter(User.id == skill.created_by).first()
        skill_dict["creator_name"] = creator.full_name or creator.username if creator else "Unknown"

        # 检查是否已收藏
        if current_user:
            saved = db.query(SavedSkill).filter(
                SavedSkill.user_id == current_user.id,
                SavedSkill.skill_id == skill.id,
            ).first()
            skill_dict["is_saved"] = saved is not None

            # 获取用户评分
            rating = db.query(SkillRating).filter(
                SkillRating.user_id == current_user.id,
                SkillRating.skill_id == skill.id,
            ).first()
            skill_dict["user_rating"] = rating.rating if rating else None
        else:
            skill_dict["is_saved"] = False
            skill_dict["user_rating"] = None

        result.append(SkillMarketResponse(**skill_dict))

    return result


@router.get("/skills/{skill_id}", response_model=SkillMarketResponse)
async def get_marketplace_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Any:
    """
    获取技能市场详情

    Args:
        skill_id: 技能 ID
        db: 数据库会话
        current_user: 当前登录用户 (可选)

    Returns:
        SkillMarketResponse: 技能详情

    Raises:
        HTTPException: 技能不存在或无权限
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    # 检查权限
    if not _can_access_skill(skill, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this skill",
        )

    skill_dict = SkillMarketResponse.model_validate(skill).model_dump()

    # 添加创建者名称
    creator = db.query(User).filter(User.id == skill.created_by).first()
    skill_dict["creator_name"] = creator.full_name or creator.username if creator else "Unknown"

    # 检查是否已收藏
    if current_user:
        saved = db.query(SavedSkill).filter(
            SavedSkill.user_id == current_user.id,
            SavedSkill.skill_id == skill.id,
        ).first()
        skill_dict["is_saved"] = saved is not None

        # 获取用户评分
        rating = db.query(SkillRating).filter(
            SkillRating.user_id == current_user.id,
            SkillRating.skill_id == skill.id,
        ).first()
        skill_dict["user_rating"] = rating.rating if rating else None
    else:
        skill_dict["is_saved"] = False
        skill_dict["user_rating"] = None

    return SkillMarketResponse(**skill_dict)


@router.post("/skills/{skill_id}/try", response_model=TrySkillResponse)
async def try_skill(
    skill_id: int,
    request: TrySkillRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> Any:
    """
    试用技能（无需登录）

    Args:
        skill_id: 技能 ID
        request: 试用请求
        db: 数据库会话
        current_user: 当前登录用户 (可选)

    Returns:
        TrySkillResponse: 执行结果

    Raises:
        HTTPException: 技能不存在或无权限
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    # 检查权限
    if not _can_access_skill(skill, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this skill",
        )

    # 调用 Agent 执行服务
    from services.agent_service import execute_agent

    try:
        start_time = time.time()

        # 使用 skill 的元数据中的配置
        system_prompt = None
        if skill.meta and "description" in skill.meta:
            system_prompt = f"You are a specialized agent with the following skill: {skill.meta['description']}"

        result = await execute_agent(
            message=request.message,
            model_name="qwen-max",
            temperature=0.7,
            max_tokens=2048,
            system_prompt=system_prompt,
        )

        execution_time = time.time() - start_time

        # 增加使用次数
        skill.usage_count += 1
        db.commit()

        return TrySkillResponse(
            status=result["status"],
            output_message=result["output_message"],
            error_message=result["error_message"],
            execution_time=execution_time,
        )

    except Exception as e:
        return TrySkillResponse(
            status="error",
            error_message=str(e),
            execution_time=0,
        )


@router.post("/skills/{skill_id}/create-agent", response_model=AgentResponse)
async def create_agent_from_skill(
    skill_id: int,
    request: CreateAgentFromSkillRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    从技能一键创建代理

    Args:
        skill_id: 技能 ID
        request: 创建请求
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        AgentResponse: 创建的代理

    Raises:
        HTTPException: 技能不存在或无权限
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    # 检查权限
    if not _can_access_skill(skill, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this skill",
        )

    # 构建 system_prompt
    system_prompt = f"You are an agent specialized in using the '{skill.name}' skill."
    if skill.meta and "description" in skill.meta:
        system_prompt += f"\n\nSkill description: {skill.meta['description']}"

    # 创建代理
    agent = Agent(
        name=request.agent_name,
        description=request.description or f"Agent using skill: {skill.name}",
        model_name=request.model_name,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        system_prompt=system_prompt,
        created_by=current_user.id,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)

    # 关联技能
    agent_skill = AgentSkill(
        agent_id=agent.id,
        skill_id=skill.id,
        enabled=True,
    )
    db.add(agent_skill)
    db.commit()
    db.refresh(agent)

    # 增加技能使用次数
    skill.usage_count += 1
    db.commit()

    # 构建响应
    agent_dict = AgentResponse.model_validate(agent).model_dump()
    agent_dict["skills"] = [SkillMarketResponse.model_validate(skill).model_dump()]

    return AgentResponse(**agent_dict)


@router.post("/skills/{skill_id}/save", status_code=status.HTTP_201_CREATED)
async def save_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    收藏技能

    Args:
        skill_id: 技能 ID
        db: 数据库会话
        current_user: 当前登录用户

    Raises:
        HTTPException: 技能不存在或已收藏

    Returns:
        dict: 成功消息
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    # 检查是否已收藏
    existing = db.query(SavedSkill).filter(
        SavedSkill.user_id == current_user.id,
        SavedSkill.skill_id == skill.id,
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill already saved",
        )

    # 创建收藏记录
    saved_skill = SavedSkill(
        user_id=current_user.id,
        skill_id=skill.id,
    )
    db.add(saved_skill)
    db.commit()

    return {"message": "Skill saved successfully"}


@router.delete("/skills/{skill_id}/save", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    取消收藏技能

    Args:
        skill_id: 技能 ID
        db: 数据库会话
        current_user: 当前登录用户

    Raises:
        HTTPException: 技能不存在或未收藏
    """
    saved_skill = db.query(SavedSkill).filter(
        SavedSkill.user_id == current_user.id,
        SavedSkill.skill_id == skill_id,
    ).first()

    if not saved_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved skill not found",
        )

    db.delete(saved_skill)
    db.commit()


@router.post("/skills/{skill_id}/rate", response_model=RatingResponse)
async def rate_skill(
    skill_id: int,
    request: RateSkillRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    评分技能

    Args:
        skill_id: 技能 ID
        request: 评分请求
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        RatingResponse: 评分结果

    Raises:
        HTTPException: 技能不存在
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    # 检查是否已评分
    existing = db.query(SkillRating).filter(
        SkillRating.user_id == current_user.id,
        SkillRating.skill_id == skill.id,
    ).first()

    if existing:
        # 更新评分
        existing.rating = request.rating
        existing.comment = request.comment
        db.commit()
        db.refresh(existing)
        rating = existing
    else:
        # 创建新评分
        rating = SkillRating(
            user_id=current_user.id,
            skill_id=skill.id,
            rating=request.rating,
            comment=request.comment,
        )
        db.add(rating)
        db.commit()
        db.refresh(rating)

    # 更新技能的平均评分
    avg_rating = db.query(func.avg(SkillRating.rating)).filter(
        SkillRating.skill_id == skill.id
    ).scalar()

    skill.rating = round(float(avg_rating), 2) if avg_rating else None
    skill.rating_count = db.query(SkillRating).filter(
        SkillRating.skill_id == skill.id
    ).count()
    db.commit()

    return RatingResponse.model_validate(rating)


@router.get("/my/saved", response_model=List[SkillMarketResponse])
async def get_my_saved_skills(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取我收藏的技能列表

    Args:
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        List[SkillMarketResponse]: 收藏的技能列表
    """
    query = db.query(Skill).join(SavedSkill).filter(
        SavedSkill.user_id == current_user.id,
    )

    skills = query.order_by(SavedSkill.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for skill in skills:
        skill_dict = SkillMarketResponse.model_validate(skill).model_dump()
        skill_dict["is_saved"] = True

        # 添加创建者名称
        creator = db.query(User).filter(User.id == skill.created_by).first()
        skill_dict["creator_name"] = creator.full_name or creator.username if creator else "Unknown"

        # 获取用户评分
        rating = db.query(SkillRating).filter(
            SkillRating.user_id == current_user.id,
            SkillRating.skill_id == skill.id,
        ).first()
        skill_dict["user_rating"] = rating.rating if rating else None

        result.append(SkillMarketResponse(**skill_dict))

    return result
