from typing import Any, Dict, List, Optional

from config.settings import BASE_DIR
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


class VectorStore:
    """三种模式的向量数据库客户端。
    
    - none: 简易内存实现（早期逻辑调试）
    - chroma: 本地轻量向量库（笔记本开发模式）
    - milvus: 生产级向量服务（服务器生产模式）
    """

    def __init__(self, backend: str = "chroma", url: Optional[str] = None) -> None:
        self.backend = backend
        self.url = url
        self._memory_store: Dict[str, List[Dict[str, Any]]] = {}
        self._chroma_client = None
        
        if self.backend == "none":
            logger.info("VectorStore using memory backend (dev mode)")
        elif self.backend == "chroma":
            self._init_chroma()
        elif self.backend == "milvus":
            # TODO: 初始化 Milvus 客户端
            logger.warning("milvus backend not implemented yet")

    def _init_chroma(self) -> None:
        """初始化 Chroma 本地向量库。"""
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            
            # 使用本地持久化存储
            chroma_dir = BASE_DIR / "data" / "chroma_db"
            chroma_dir.mkdir(parents=True, exist_ok=True)
            
            self._chroma_client = chromadb.PersistentClient(
                path=str(chroma_dir),
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            logger.info(f"Chroma initialized at {chroma_dir}")
        except ImportError:
            logger.error(
                "chromadb not installed. Install with: pip install chromadb\n"
                "Falling back to memory backend."
            )
            self.backend = "none"
        except Exception as e:
            logger.error(f"Failed to initialize Chroma: {e}. Falling back to memory backend.")
            self.backend = "none"

    async def insert(self, collection: str, vectors: List[List[float]], metadata: List[dict]) -> None:
        """插入向量。"""
        if self.backend == "none":
            self._memory_insert(collection, vectors, metadata)
        elif self.backend == "chroma":
            self._chroma_insert(collection, vectors, metadata)
        elif self.backend == "milvus":
            # TODO: 调用 Milvus API
            logger.warning("milvus insert not implemented")

    def _memory_insert(self, collection: str, vectors: List[List[float]], metadata: List[dict]) -> None:
        """内存模式：简单存储。"""
        if collection not in self._memory_store:
            self._memory_store[collection] = []
        
        for i, (vec, meta) in enumerate(zip(vectors, metadata)):
            self._memory_store[collection].append({
                "id": f"{collection}_{len(self._memory_store[collection])}",
                "vector": vec,
                "metadata": meta
            })
        
        logger.info(f"Memory insert: {len(vectors)} vectors into {collection}")

    def _chroma_insert(self, collection: str, vectors: List[List[float]], metadata: List[dict]) -> None:
        """使用 Chroma 插入向量。"""
        if not self._chroma_client:
            logger.error("Chroma client not initialized")
            return
        
        try:
            coll = self._chroma_client.get_or_create_collection(name=collection)
            
            # 生成 ID
            ids = [f"{collection}_{i}_{hash(str(meta))}" for i, meta in enumerate(metadata)]
            
            # Chroma 需要 documents 字段（如果 metadata 有 text）
            documents = [meta.get("text", "") for meta in metadata]
            
            coll.add(
                ids=ids,
                embeddings=vectors,
                metadatas=metadata,
                documents=documents
            )
            logger.info(f"Chroma insert: {len(vectors)} vectors into {collection}")
        except Exception as e:
            logger.error(f"Chroma insert failed: {e}")

    async def search(self, collection: str, query_vector: List[float], top_k: int = 5) -> List[dict]:
        """检索相似向量。"""
        if self.backend == "none":
            return self._memory_search(collection, query_vector, top_k)
        elif self.backend == "chroma":
            return self._chroma_search(collection, query_vector, top_k)
        elif self.backend == "milvus":
            # TODO: 调用 Milvus API
            logger.warning("milvus search not implemented")
            return []
        else:
            return []

    def _memory_search(self, collection: str, query_vector: List[float], top_k: int) -> List[dict]:
        """内存模式：简易相似度计算。"""
        items = self._memory_store.get(collection, [])
        if not items:
            return []
        
        # 简化版：计算余弦相似度
        import math
        
        def cosine_similarity(v1: List[float], v2: List[float]) -> float:
            dot = sum(a * b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a * a for a in v1))
            norm2 = math.sqrt(sum(b * b for b in v2))
            return dot / (norm1 * norm2) if norm1 and norm2 else 0.0
        
        scores = [(item, cosine_similarity(query_vector, item["vector"])) for item in items]
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = [{"metadata": item["metadata"], "score": score} for item, score in scores[:top_k]]
        logger.info(f"Memory search: {len(results)} results from {collection}")
        return results

    def _chroma_search(self, collection: str, query_vector: List[float], top_k: int) -> List[dict]:
        """使用 Chroma 检索。"""
        if not self._chroma_client:
            logger.error("Chroma client not initialized")
            return []
        
        try:
            coll = self._chroma_client.get_collection(name=collection)
            results = coll.query(
                query_embeddings=[query_vector],
                n_results=top_k
            )
            
            # 转换为统一格式
            output = []
            if results and results["metadatas"] and results["distances"]:
                for meta, distance in zip(results["metadatas"][0], results["distances"][0]):
                    output.append({
                        "metadata": meta,
                        "score": 1.0 - distance  # Chroma 返回距离，转为相似度
                    })
            
            logger.info(f"Chroma search: {len(output)} results from {collection}")
            return output
        except Exception as e:
            logger.error(f"Chroma search failed: {e}")
            return []
