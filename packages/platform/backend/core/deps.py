"""
依赖注入：用于 FastAPI 的依赖项
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from db.session import get_db
from db.models import User
from core.security import decode_access_token
from models.schemas import TokenData

# HTTP Bearer 认证（自动模式）
security = HTTPBearer()

# HTTP Bearer 认证（可选模式）
security_optional = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前登录用户

    Args:
        credentials: HTTP Bearer credentials
        db: 数据库会话

    Returns:
        User: 当前用户

    Raises:
        HTTPException: 认证失败时抛出 401 错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # 解码 Token
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    user_id: Optional[int] = payload.get("sub")

    if user_id is None:
        raise credentials_exception

    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前活跃用户

    Args:
        current_user: 当前用户

    Returns:
        User: 当前活跃用户

    Raises:
        HTTPException: 用户不活跃时抛出 403 错误
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return current_user


def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前超级用户

    Args:
        current_user: 当前用户

    Returns:
        User: 当前超级用户

    Raises:
        HTTPException: 用户不是超级用户时抛出 403 错误
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    获取当前登录用户（可选）

    允许未登录用户访问，但如果有 token 则返回用户信息

    Args:
        credentials: HTTP Bearer credentials（可选）
        db: 数据库会话

    Returns:
        Optional[User]: 当前用户，如果未登录则返回 None
    """
    if credentials is None:
        return None

    token = credentials.credentials

    # 解码 Token
    payload = decode_access_token(token)

    if payload is None:
        return None

    user_id: Optional[int] = payload.get("sub")

    if user_id is None:
        return None

    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()

    if user is None or not user.is_active:
        return None

    return user
