"""知识层统一初始化。"""
from config.settings import settings
from shared.knowledge.vector_store import VectorStore
from shared.knowledge.rag_engine import RAGEngine

# 根据配置初始化向量库
vector_store = VectorStore(
    backend=settings.service_config.vector_backend,
    url=settings.service_config.vector_url
)

# RAG 引擎（后续实现）
rag_engine = RAGEngine(vector_store=vector_store)

__all__ = ["vector_store", "rag_engine"]
