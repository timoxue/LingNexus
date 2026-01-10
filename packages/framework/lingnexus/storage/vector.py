"""
向量数据库模块

使用ChromaDB实现向量存储和语义检索，支持RAG查询
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from pathlib import Path


class VectorDB:
    """向量数据库管理器（基于ChromaDB）"""

    def __init__(self, persist_dir: str = "data/vectordb", collection_name: str = "intelligence"):
        """
        初始化向量数据库

        Args:
            persist_dir: 数据持久化目录
            collection_name: 集合名称
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # 创建ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "竞品情报向量数据库"}
        )

    def add(
        self,
        data_id: str,
        text: str,
        metadata: Dict,
        embed_id: Optional[str] = None
    ) -> bool:
        """
        添加文档到向量数据库

        Args:
            data_id: 原始数据ID
            text: 文档文本内容
            metadata: 元数据字典
            embed_id: 自定义嵌入ID（可选，默认使用data_id）

        Returns:
            是否成功
        """
        try:
            doc_id = embed_id or data_id

            self.collection.add(
                documents=[text],
                metadatas=[{
                    "data_id": data_id,
                    "source": metadata.get("source"),
                    "project": metadata.get("project"),
                    "collected_at": metadata.get("collected_at"),
                    "url": metadata.get("url"),
                    "nct_id": metadata.get("extracted_data", {}).get("nct_id"),
                    "company": metadata.get("extracted_data", {}).get("company"),
                    "status": metadata.get("extracted_data", {}).get("status"),
                    **metadata
                }],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            print(f"Error adding to vector DB: {e}")
            return False

    def search(
        self,
        query: str,
        n_results: int = 10,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """
        语义搜索

        Args:
            query: 搜索查询文本
            n_results: 返回结果数量
            filter: 过滤条件（如 {"project": "司美格鲁肽"}）

        Returns:
            搜索结果列表
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter
            )

            # 格式化结果
            formatted_results = []
            if results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    result = {
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                    }

                    # 添加距离（如果有的话）
                    if 'distances' in results and results['distances']:
                        result["distance"] = results['distances'][0][i]
                        result["similarity"] = 1 - result["distance"]

                    formatted_results.append(result)

            return formatted_results
        except Exception as e:
            print(f"Error searching vector DB: {e}")
            return []

    def get(self, data_id: str) -> Optional[Dict]:
        """
        根据ID获取文档

        Args:
            data_id: 数据ID

        Returns:
            文档内容或None
        """
        try:
            results = self.collection.get(
                ids=[data_id],
                include=["documents", "metadatas"]
            )

            if results['ids'] and len(results['ids']) > 0:
                return {
                    "id": results['ids'][0],
                    "document": results['documents'][0],
                    "metadata": results['metadatas'][0]
                }
            return None
        except Exception as e:
            print(f"Error getting from vector DB: {e}")
            return None

    def delete(self, data_id: str) -> bool:
        """
        删除文档

        Args:
            data_id: 数据ID

        Returns:
            是否成功
        """
        try:
            self.collection.delete(ids=[data_id])
            return True
        except Exception as e:
            print(f"Error deleting from vector DB: {e}")
            return False

    def update(
        self,
        data_id: str,
        text: str,
        metadata: Dict
    ) -> bool:
        """
        更新文档（先删除再添加）

        Args:
            data_id: 数据ID
            text: 新的文档文本
            metadata: 新的元数据

        Returns:
            是否成功
        """
        try:
            # 先删除
            self.delete(data_id)
            # 再添加
            return self.add(data_id, text, metadata)
        except Exception as e:
            print(f"Error updating vector DB: {e}")
            return False

    def count(self) -> int:
        """
        获取文档总数

        Returns:
            文档数量
        """
        try:
            return self.collection.count()
        except Exception:
            return 0

    def clear(self) -> bool:
        """
        清空集合

        Returns:
            是否成功
        """
        try:
            # 删除并重新创建集合
            collection_name = self.collection.name
            self.client.delete_collection(collection_name)
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "竞品情报向量数据库"}
            )
            return True
        except Exception as e:
            print(f"Error clearing vector DB: {e}")
            return False

    def get_all_projects(self) -> List[str]:
        """
        获取所有项目名称

        Returns:
            项目名称列表
        """
        try:
            # 获取所有文档的元数据
            results = self.collection.get(
                include=["metadatas"]
            )

            if not results['metadatas']:
                return []

            # 提取所有不重复的项目名
            projects = set()
            for meta in results['metadatas']:
                if meta.get('project'):
                    projects.add(meta['project'])

            return sorted(list(projects))
        except Exception as e:
            print(f"Error getting projects: {e}")
            return []
