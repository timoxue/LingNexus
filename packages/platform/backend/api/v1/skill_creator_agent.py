"""
Skill Creator Agent API 端点

提供 Agent 会话管理和对话接口
"""
from typing import Any, Dict, Optional
import logging
import os

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.session import get_db
from db.models import User
from core.deps import get_current_active_user, get_bypass_current_user
from services.skill_creator_agent_service import get_skill_creator_agent_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/skill-creator-agent", tags=["Skill Creator Agent"])


@router.get("/test")
async def test_endpoint() -> Any:
    """测试端点，绕过认证"""
    return {"message": "Test endpoint works", "status": "ok"}


class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    use_api_key: bool = False


class ChatRequest(BaseModel):
    """对话请求"""
    session_id: str
    message: str


@router.post("/session/create")
async def create_session(
    request: CreateSessionRequest,
    # Temporarily bypass authentication for testing
    # current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新的 Skill Creator Agent 会话

    返回第一个问题，开始渐进式愿景定义流程

    Returns:
        会话信息和第一个问题
    """
    try:
        logger.info(f"===== CREATE SESSION REQUEST =====")
        logger.info(f"Request: use_api_key={request.use_api_key}")

        service = get_skill_creator_agent_service()

        # 获取 API Key（如果用户选择使用）
        api_key = None
        if request.use_api_key:
            api_key = os.getenv("DASHSCOPE_API_KEY")
            logger.info(f"Using API key from environment")

        logger.info(f"Calling service.create_session...")
        response = await service.create_session(
            user_id=1,  # Test user ID
            api_key=api_key,
        )

        logger.info(f"Created agent session {response['session_id']} for test user")
        return response

    except Exception as e:
        logger.error(f"===== CREATE SESSION ERROR =====")
        logger.error(f"Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}",
        )


@router.post("/chat")
async def chat(
    request: ChatRequest,
    # Temporarily bypass authentication for testing
    current_user: User = Depends(get_bypass_current_user),
) -> Any:
    """
    与 Skill Creator Agent 对话

    处理用户的回答，返回下一个问题或总结

    Returns:
        Agent 响应（下一个问题或总结）
    """
    try:
        service = get_skill_creator_agent_service()

        response = await service.chat(
            session_id=request.session_id,
            message=request.message,
            user_id=1,  # Test user ID
        )

        logger.info(f"Chat in session {request.session_id}, q={response.get('question_number') or 'summary'}")
        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}",
        )


@router.post("/session/end")
async def end_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    结束 Agent 会话

    保存技能元数据并清理会话

    Returns:
        最终的技能元数据
    """
    try:
        service = get_skill_creator_agent_service()

        response = await service.end_session(
            session_id=session_id,
            user_id=1,  # Test user ID
        )

        logger.info(f"Ended session {session_id} for test user")
        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end session: {str(e)}",
        )


@router.get("/session/{session_id}")
async def get_session_status(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取会话状态

    Returns:
        会话状态信息
    """
    try:
        service = get_skill_creator_agent_service()
        session = service.sessions.get(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )

        if session.user_id != 1:  # Test user ID
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized for this session",
            )

        return {
            "session_id": session.session_id,
            "current_dimension_idx": session.current_dimension_idx,
            "current_dimension": session.current_dimension,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "is_expired": session.is_expired(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session status: {str(e)}",
        )


@router.post("/session/{session_id}/save-skill")
async def save_skill_from_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    从会话保存技能到数据库

    基于会话收集的元数据创建技能记录

    Returns:
        创建的技能信息
    """
    try:
        service = get_skill_creator_agent_service()
        session = service.sessions.get(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )

        if session.user_id != 1:  # Test user ID
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized for this session",
            )

        # 生成元数据
        metadata = service._generate_metadata(session.answers)

        # 构建 SKILL.md 内容
        skill_md_content = f"""---
name: {metadata['skill_name']}
description: {metadata['core_value']}
main_alias: {metadata['main_alias']}
category: {metadata['category']}
---

# {metadata['skill_name'].replace('-', ' ').title()}

## 💡 快速开始

```
{metadata['main_alias']} [参数]
```

## 📱 所有可用别名

| 类型 | 调用方式 | 示例 | 说明 |
|------|----------|------|------|
| **主别名** | 自然语言 | `{metadata['main_alias']} ...` | 最常用 |
{chr(10).join(f"| 上下文别名 | 自然语言 | `{alias}` | 专用场景 |" for alias in metadata['context_aliases'])}
| **命令别名** | 快捷命令 | `/{metadata['command_alias']} ...` | 高级用法 |
| **API别名** | 程序调用 | `{metadata['api_alias']}` | 系统集成 |

## 🎯 核心价值

{metadata['core_value']}

## 📋 使用场景

{metadata['usage_scenario']}

## ⚠️ 边界与限制

{metadata['boundaries']}

## 🎯 目标用户

{', '.join(metadata['target_users'])}

## 🔧 建议能力

{chr(10).join(f"- **{cap['name']}** (复杂度: {cap['complexity']})" for cap in metadata['suggested_capabilities'])}
"""

        # 创建技能记录
        from db.models import Skill

        skill = Skill(
            name=metadata['skill_name'],
            category="internal",
            content=skill_md_content,
            meta={
                "main_alias": metadata['main_alias'],
                "context_aliases": metadata['context_aliases'],
                "command_alias": metadata['command_alias'],
                "api_alias": metadata['api_alias'],
                "target_users": metadata['target_users'],
                "compliance_requirements": metadata['compliance_requirements'],
                "session_id": session_id,
            },
            is_active=True,
            version="1.0.0",
            created_by=1,  # Test user ID
            sharing_scope="private",
            is_official=False,
        )

        db.add(skill)
        db.commit()
        db.refresh(skill)

        logger.info(f"Saved skill '{skill.name}' (ID: {skill.id}) from session {session_id}")

        return {
            "skill_id": skill.id,
            "skill_name": skill.name,
            "message": "技能保存成功",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving skill: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save skill: {str(e)}",
        )
