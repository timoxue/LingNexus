"""
原始数据存储模块

负责保存爬取的完整原始数据（HTML/JSON），支持数据追溯
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple


class RawStorage:
    """原始数据存储管理器"""

    def __init__(self, base_dir: str = "data/raw"):
        """
        初始化原始数据存储

        Args:
            base_dir: 基础目录路径
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        source: str,
        data: str,
        url: str,
        project: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        保存原始数据

        Args:
            source: 数据源名称（CDE/Insight/ClinicalTrials等）
            data: 原始数据内容（HTML或JSON字符串）
            url: 数据来源URL
            project: 项目名称
            metadata: 额外的元数据

        Returns:
            data_id: 生成的数据ID
        """
        # 生成数据ID和哈希
        data_hash = hashlib.sha256(data.encode()).hexdigest()[:12]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_id = f"{source.lower()}_{timestamp}_{data_hash}"

        # 创建目录
        date_str = datetime.now().strftime("%Y-%m-%d")
        source_dir = self.base_dir / source.lower() / date_str
        source_dir.mkdir(parents=True, exist_ok=True)

        # 判断数据类型
        data_type = "json" if data.strip().startswith('{') else "html"
        file_ext = "json" if data_type == "json" else "html"

        # 保存原始数据
        file_path = source_dir / f"{data_id}.{file_ext}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)

        # 构建元数据
        meta = {
            "data_id": data_id,
            "source": source,
            "url": url,
            "project": project,
            "collected_at": datetime.now().isoformat(),
            "data_type": data_type,
            "file_path": str(file_path),
            "file_size": len(data),
            "hash": f"sha256:{data_hash}",
            **(metadata or {})
        }

        # 保存元数据
        meta_path = source_dir / f"{data_id}.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        return data_id

    def load(self, data_id: str) -> Optional[Tuple[str, Dict]]:
        """
        加载原始数据

        Args:
            data_id: 数据ID

        Returns:
            (原始数据内容, 元数据) 或 None
        """
        # 从data_id中提取信息
        # 格式: source_YYYYMMDD_HHMMSS_hash
        parts = data_id.split('_')
        if len(parts) < 4:
            return None

        source = parts[0]
        date_parts = parts[1]  # YYYYMMDD

        # 转换日期格式: YYYYMMDD -> YYYY-MM-DD
        if len(date_parts) == 8:
            date_str = f"{date_parts[:4]}-{date_parts[4:6]}-{date_parts[6:8]}"
        else:
            return None

        # 查找目录
        source_dir = self.base_dir / source.lower()
        date_dir = source_dir / date_str

        if not date_dir.exists():
            return None

        # 查找文件
        data_file = date_dir / f"{data_id}.html"
        meta_file = date_dir / f"{data_id}.json"

        if not data_file.exists():
            data_file = date_dir / f"{data_id}.json"

        if data_file.exists() and meta_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = f.read()

            with open(meta_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            return data, metadata

        return None

    def list_by_date(self, source: str, date: str) -> list:
        """
        列出指定日期的所有数据

        Args:
            source: 数据源名称
            date: 日期（YYYY-MM-DD格式）

        Returns:
            元数据列表
        """
        date_dir = self.base_dir / source.lower() / date
        if not date_dir.exists():
            return []

        results = []
        for meta_file in date_dir.glob("*.json"):
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                    results.append(meta)
            except Exception as e:
                print(f"Error loading {meta_file}: {e}")

        return results

    def list_by_project(self, project: str, limit: int = 100) -> list:
        """
        列出指定项目的所有数据

        Args:
            project: 项目名称
            limit: 返回数量限制

        Returns:
            元数据列表
        """
        results = []

        # 遍历所有数据源
        for source_dir in self.base_dir.iterdir():
            if not source_dir.is_dir():
                continue

            # 遍历所有日期
            for date_dir in source_dir.iterdir():
                if not date_dir.is_dir():
                    continue

                for meta_file in date_dir.glob("*.json"):
                    try:
                        with open(meta_file, 'r', encoding='utf-8') as f:
                            meta = json.load(f)

                            if meta.get('project') == project:
                                results.append(meta)

                                if len(results) >= limit:
                                    return results
                    except Exception:
                        continue

        # 按时间排序（最新的在前）
        results.sort(key=lambda x: x.get('collected_at', ''), reverse=True)
        return results

    def delete_old_data(self, days: int = 30):
        """
        删除旧数据

        Args:
            days: 保留天数
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for source_dir in self.base_dir.iterdir():
            if not source_dir.is_dir():
                continue

            for date_dir in source_dir.iterdir():
                if not date_dir.is_dir():
                    continue

                # 解析日期
                try:
                    dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")

                    if dir_date < cutoff_date:
                        # 删除整个目录
                        import shutil
                        shutil.rmtree(date_dir)
                        deleted_count += 1
                        print(f"Deleted old data: {date_dir}")
                except ValueError:
                    continue

        return deleted_count
