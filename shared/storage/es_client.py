import json
from pathlib import Path
from typing import Any, Dict, Optional

from config.settings import BASE_DIR
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


class ESClient:
    """两种模式的 Elasticsearch 客户端。
    
    - local_file: 从本地 JSON 文件读取数据（笔记本开发模式）
    - remote_es: 连接真实 ES 服务（服务器生产模式）
    """

    def __init__(self, backend: str = "local_file", url: Optional[str] = None) -> None:
        self.backend = backend
        self.url = url
        self._local_data: Dict[str, list] = {}
        
        if self.backend == "local_file":
            self._load_local_data()
        elif self.backend == "remote_es":
            # TODO: 初始化真实 ES 客户端（elasticsearch-py）
            logger.warning("remote_es backend not implemented yet")

    def _load_local_data(self) -> None:
        """加载本地测试数据。"""
        data_dir = BASE_DIR / "data"
        data_dir.mkdir(exist_ok=True)
        
        # 加载临床试验数据
        clinical_trials_file = data_dir / "clinical_trials.json"
        if clinical_trials_file.exists():
            with clinical_trials_file.open("r", encoding="utf-8") as f:
                self._local_data["clinical_trials"] = json.load(f)
                logger.info(f"Loaded {len(self._local_data['clinical_trials'])} clinical trials from local file")
        else:
            self._local_data["clinical_trials"] = []
            logger.warning(f"Clinical trials file not found: {clinical_trials_file}")

        # 加载医药资讯数据（订阅日报用）
        pharma_news_file = data_dir / "pharma_news.json"
        if pharma_news_file.exists():
            with pharma_news_file.open("r", encoding="utf-8") as f:
                self._local_data["pharma_news"] = json.load(f)
                logger.info(f"Loaded {len(self._local_data['pharma_news'])} pharma news items from local file")
        else:
            self._local_data["pharma_news"] = []
            logger.warning(f"Pharma news file not found: {pharma_news_file}")
        
        # 预留其他数据集加载逻辑
        logger.info("Local file backend initialized", extra={"indexes": list(self._local_data.keys())})

    async def search(self, index: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """执行搜索请求。"""
        if self.backend == "local_file":
            return self._local_search(index, query)
        elif self.backend == "remote_es":
            # TODO: 调用真实 ES API
            logger.warning("remote_es search not implemented")
            return {"hits": []}
        else:
            return {"hits": []}

    def _local_search(self, index: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """本地文件简易搜索（关键词匹配）。"""
        data = self._local_data.get(index, [])
        
        # 提取搜索关键词（简化处理）
        keyword = ""
        if "query" in query:
            if "match" in query["query"]:
                # 支持 {"query": {"match": {"field": "keyword"}}}
                for field, value in query["query"]["match"].items():
                    keyword = str(value).lower()
                    break
            elif "query_string" in query["query"]:
                # 支持 {"query": {"query_string": {"query": "keyword"}}}
                keyword = query["query"]["query_string"].get("query", "").lower()
        
        # 简易全文匹配
        results = []
        for item in data:
            item_str = json.dumps(item, ensure_ascii=False).lower()
            if not keyword or keyword in item_str:
                results.append(item)
        
        logger.info("Local search executed", extra={
            "index": index,
            "keyword": keyword,
            "total_docs": len(data),
            "matched": len(results)
        })
        
        return {"hits": results[:50]}  # 限制返回 50 条

    async def get(self, index: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """获取单条文档。"""
        if self.backend == "local_file":
            data = self._local_data.get(index, [])
            for item in data:
                if item.get("id") == doc_id or item.get("_id") == doc_id:
                    return item
            return None
        elif self.backend == "remote_es":
            # TODO: 调用真实 ES API
            logger.warning("remote_es get not implemented")
            return None
        else:
            return None
