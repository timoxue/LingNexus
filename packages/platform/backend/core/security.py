"""
安全相关功能：密码哈希、JWT Token 生成和验证
"""
from datetime import datetime, timedelta
from typing import Optional
import hashlib

from jose import JWTError, jwt

# JWT 配置
SECRET_KEY = "your-secret-key-change-this-in-production"  # 生产环境应从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码

    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码

    Returns:
        bool: 密码是否匹配
    """
    # 简单的 SHA256 哈希（仅用于开发，生产环境请使用 bcrypt）
    hash_input = f"{plain_password}{SECRET_KEY}"
    computed_hash = hashlib.sha256(hash_input.encode()).hexdigest()
    return computed_hash == hashed_password


def get_password_hash(password: str) -> str:
    """
    生成密码哈希

    Args:
        password: 明文密码

    Returns:
        str: 哈希密码
    """
    # 简单的 SHA256 哈希（仅用于开发，生产环境请使用 bcrypt）
    hash_input = f"{password}{SECRET_KEY}"
    return hashlib.sha256(hash_input.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT Token

    Args:
        data: 要编码的数据 (通常包含 sub: user_id)
        expires_delta: 过期时间增量

    Returns:
        str: JWT Token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码 JWT Token

    Args:
        token: JWT Token

    Returns:
        Optional[dict]: 解码后的数据，如果失败返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
