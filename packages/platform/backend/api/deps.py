"""
API dependencies
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from db.session import get_db


def get_db_session():
    """获取数据库会话"""
    return Depends(get_db)
