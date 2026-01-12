"""
代理管理 API 端点
"""
import time
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.session import get_db
from db.models import User, Agent, Skill, AgentSkill, AgentExecution
from core.deps import get_current_active_user
from models.schemas import AgentCreate, AgentUpdate, AgentResponse, AgentExecute, AgentExecuteResponse, ExecutionResponse

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    is_active: bool = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db),
) -> Any:
    """
    获取代理列表

    Args:
        is_active: 是否活跃过滤
        skip: 跳过记录数
        limit: 返回记录数
        db: 数据库会话

    Returns:
        List[AgentResponse]: 代理列表
    """
    query = db.query(Agent)

    # 应用过滤条件
    if is_active is not None:
        query = query.filter(Agent.is_active == is_active)

    # 分页
    agents = query.order_by(Agent.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for agent in agents:
        # 加载关联的技能
        agent_dict = AgentResponse.model_validate(agent).model_dump()
        agent_skills = db.query(AgentSkill).filter(
            AgentSkill.agent_id == agent.id,
            AgentSkill.enabled == True
        ).all()

        skills = []
        for agent_skill in agent_skills:
            skill = db.query(Skill).filter(Skill.id == agent_skill.skill_id).first()
            if skill:
                skills.append({
                    "id": skill.id,
                    "name": skill.name,
                    "category": skill.category,
                })

        agent_dict["skills"] = skills
        result.append(agent_dict)

    return result


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """
    获取单个代理详情

    Args:
        agent_id: 代理 ID
        db: 数据库会话

    Returns:
        AgentResponse: 代理详情

    Raises:
        HTTPException: 代理不存在
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # 加载关联的技能
    agent_dict = AgentResponse.model_validate(agent).model_dump()
    agent_skills = db.query(AgentSkill).filter(
        AgentSkill.agent_id == agent.id,
        AgentSkill.enabled == True
    ).all()

    skills = []
    for agent_skill in agent_skills:
        skill = db.query(Skill).filter(Skill.id == agent_skill.skill_id).first()
        if skill:
            skills.append({
                "id": skill.id,
                "name": skill.name,
                "category": skill.category,
            })

    agent_dict["skills"] = skills

    return agent_dict


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_in: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新代理

    Args:
        agent_in: 代理创建信息
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        AgentResponse: 创建的代理
    """
    # 检查代理名是否已存在
    existing_agent = db.query(Agent).filter(Agent.name == agent_in.name).first()
    if existing_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent name already exists",
        )

    # 创建代理
    agent = Agent(
        name=agent_in.name,
        description=agent_in.description,
        model_name=agent_in.model_name,
        temperature=agent_in.temperature,
        max_tokens=agent_in.max_tokens,
        system_prompt=agent_in.system_prompt,
        created_by=current_user.id,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)

    # 关联技能
    if agent_in.skill_ids:
        for skill_id in agent_in.skill_ids:
            # 检查技能是否存在
            skill = db.query(Skill).filter(Skill.id == skill_id).first()
            if skill:
                agent_skill = AgentSkill(
                    agent_id=agent.id,
                    skill_id=skill_id,
                    enabled=True,
                )
                db.add(agent_skill)

        db.commit()
        db.refresh(agent)

    return AgentResponse.model_validate(agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_in: AgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新代理

    Args:
        agent_id: 代理 ID
        agent_in: 代理更新信息
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        AgentResponse: 更新后的代理

    Raises:
        HTTPException: 代理不存在或无权限
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # 检查权限（只有创建者可以修改）
    if agent.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # 更新字段
    update_data = agent_in.model_dump(exclude_unset=True, exclude={"skill_ids"})
    for field, value in update_data.items():
        setattr(agent, field, value)

    db.commit()
    db.refresh(agent)

    # 更新技能关联
    if agent_in.skill_ids is not None:
        # 删除旧的关联
        db.query(AgentSkill).filter(AgentSkill.agent_id == agent.id).delete()

        # 添加新的关联
        for skill_id in agent_in.skill_ids:
            skill = db.query(Skill).filter(Skill.id == skill_id).first()
            if skill:
                agent_skill = AgentSkill(
                    agent_id=agent.id,
                    skill_id=skill_id,
                    enabled=True,
                )
                db.add(agent_skill)

        db.commit()
        db.refresh(agent)

    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    删除代理

    Args:
        agent_id: 代理 ID
        db: 数据库会话
        current_user: 当前登录用户

    Raises:
        HTTPException: 代理不存在或无权限
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # 检查权限（只有创建者可以删除）
    if agent.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    db.delete(agent)
    db.commit()


@router.post("/{agent_id}/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    agent_id: int,
    execute_request: AgentExecute,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    执行代理

    Args:
        agent_id: 代理 ID
        execute_request: 执行请求
        background_tasks: 后台任务
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        AgentExecuteResponse: 执行结果

    Raises:
        HTTPException: 代理不存在或未激活
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    if not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent is not active",
        )

    # 调用 Agent 执行服务
    from services.agent_service import execute_agent as run_agent
    from db.models import AgentExecution, AgentSkill, Skill

    # 查询 Agent 绑定的技能列表
    agent_skills_query = db.query(
        Skill.name, Skill.category
    ).join(
        AgentSkill, AgentSkill.skill_id == Skill.id
    ).filter(
        AgentSkill.agent_id == agent.id,
        AgentSkill.enabled == True
    ).all()

    bound_skills = [skill_name for (skill_name, _) in agent_skills_query]
    print(f"[DEBUG] Agent '{agent.name}' 绑定的技能: {bound_skills}")

    # 创建执行记录（状态为 running）
    execution = AgentExecution(
        agent_id=agent.id,
        input_message=execute_request.message,
        status="running",
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)

    # 执行 Agent
    try:
        print(f"[DEBUG] 开始执行 Agent: {agent.name}")
        print(f"[DEBUG] 消息: {execute_request.message}")
        print(f"[DEBUG] 模型: {agent.model_name}, 温度: {agent.temperature}")
        print(f"[DEBUG] 绑定技能: {bound_skills}")

        result = await run_agent(
            message=execute_request.message,
            model_name=agent.model_name,
            temperature=float(agent.temperature),
            max_tokens=agent.max_tokens,
            system_prompt=agent.system_prompt,
            skills=bound_skills if bound_skills else None,  # 传递技能列表
        )

        print(f"[DEBUG] Agent 执行完成，状态: {result.get('status')}")

        # 更新执行记录
        execution.status = result["status"]

        # 处理 output_message：可能是字符串、列表或字典
        output_msg = result["output_message"]
        if isinstance(output_msg, list):
            # 如果是列表，转换为字符串
            execution.output_message = str(output_msg)
        elif isinstance(output_msg, dict):
            # 如果是字典，转换为 JSON 字符串
            import json
            execution.output_message = json.dumps(output_msg, ensure_ascii=False)
        else:
            # 其他类型（包括字符串）直接赋值
            execution.output_message = output_msg

        execution.error_message = result["error_message"]
        execution.tokens_used = result["tokens_used"]
        execution.execution_time = result["execution_time"]
        execution.completed_at = func.now()
        db.commit()
        db.refresh(execution)

        return AgentExecuteResponse(
            execution_id=execution.id,
            status=execution.status,
            output_message=execution.output_message,
            error_message=execution.error_message,
            tokens_used=execution.tokens_used,
            execution_time=execution.execution_time,
        )

    except Exception as e:
        # 执行失败，更新记录
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Agent 执行失败:")
        print(f"[ERROR] {str(e)}")
        print(f"[ERROR] Traceback:\n{error_trace}")

        execution.status = "failed"
        execution.error_message = f"{str(e)}\n\n{error_trace}"
        execution.completed_at = func.now()
        db.commit()
        db.refresh(execution)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}\n\n{error_trace}",
        )


@router.get("/{agent_id}/executions", response_model=List[ExecutionResponse])
async def get_agent_executions(
    agent_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取代理执行历史

    Args:
        agent_id: 代理 ID
        skip: 跳过记录数
        limit: 返回记录数
        status: 状态过滤 (pending/running/success/failed)
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        List[ExecutionResponse]: 执行历史列表

    Raises:
        HTTPException: 代理不存在
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # 检查权限
    if agent.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    query = db.query(AgentExecution).filter(AgentExecution.agent_id == agent_id)

    # 应用状态过滤
    if status:
        query = query.filter(AgentExecution.status == status)

    # 分页并按创建时间倒序
    executions = query.order_by(AgentExecution.created_at.desc()).offset(skip).limit(limit).all()

    return [ExecutionResponse.model_validate(e) for e in executions]


@router.get("/{agent_id}/executions/{execution_id}", response_model=ExecutionResponse)
async def get_agent_execution(
    agent_id: int,
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取单条执行记录详情

    Args:
        agent_id: 代理 ID
        execution_id: 执行记录 ID
        db: 数据库会话
        current_user: 当前登录用户

    Returns:
        ExecutionResponse: 执行记录详情

    Raises:
        HTTPException: 代理或执行记录不存在
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    # 检查权限
    if agent.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    execution = db.query(AgentExecution).filter(
        AgentExecution.id == execution_id,
        AgentExecution.agent_id == agent_id,
    ).first()

    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )

    return ExecutionResponse.model_validate(execution)

