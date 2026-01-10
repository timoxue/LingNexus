"""
LingNexus 存储模块

提供原始数据、向量数据库、结构化数据库的统一存储接口
"""

from .raw import RawStorage
from .structured import StructuredDB

# VectorDB需要chromadb，变为可选依赖
try:
    from .vector import VectorDB
    _vector_available = True
except ImportError:
    VectorDB = None
    _vector_available = False

__all__ = ['RawStorage', 'StructuredDB', 'VectorDB']
