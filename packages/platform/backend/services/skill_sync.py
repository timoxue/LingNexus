"""
技能同步服务
自动从 Framework 导入技能到 Platform 数据库
"""
import yaml
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from db.models import Skill
from models.schemas import SkillResponse


class SkillSyncService:
    """技能同步服务"""

    def __init__(self, framework_path: Path):
        """
        初始化技能同步服务

        Args:
            framework_path: Framework 包路径
        """
        self.framework_path = framework_path
        self.skills_dir = framework_path / "skills"

    def sync_all_skills(
        self,
        db: Session,
        created_by: int = 1,
        force_update: bool = False
    ) -> Dict[str, any]:
        """
        同步所有技能

        Args:
            db: 数据库会话
            created_by: 创建者 ID
            force_update: 是否强制更新已存在的技能

        Returns:
            同步结果统计
        """
        stats = {
            "total": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "failed": 0,
            "errors": []
        }

        if not self.skills_dir.exists():
            stats["errors"].append(f"Skills directory not found: {self.skills_dir}")
            return stats

        # 同步 external skills
        external_dir = self.skills_dir / "external"
        if external_dir.exists():
            external_stats = self._sync_from_directory(
                db, external_dir, "external", created_by, force_update
            )
            self._merge_stats(stats, external_stats)

        # 同步 internal skills
        internal_dir = self.skills_dir / "internal"
        if internal_dir.exists():
            internal_stats = self._sync_from_directory(
                db, internal_dir, "internal", created_by, force_update
            )
            self._merge_stats(stats, internal_stats)

        return stats

    def _sync_from_directory(
        self,
        db: Session,
        directory: Path,
        category: str,
        created_by: int,
        force_update: bool
    ) -> Dict[str, any]:
        """从目录同步技能"""
        stats = {
            "total": 0,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "failed": 0,
            "errors": []
        }

        for skill_path in directory.iterdir():
            if not skill_path.is_dir():
                continue

            stats["total"] += 1

            skill_md = skill_path / "SKILL.md"
            if not skill_md.exists():
                stats["skipped"] += 1
                continue

            try:
                result = self._sync_skill(
                    db, skill_path, skill_md, category, created_by, force_update
                )

                if result == "created":
                    stats["created"] += 1
                elif result == "updated":
                    stats["updated"] += 1
                elif result == "skipped":
                    stats["skipped"] += 1

            except Exception as e:
                stats["failed"] += 1
                stats["errors"].append(f"{skill_path.name}: {str(e)}")

        return stats

    def _sync_skill(
        self,
        db: Session,
        skill_path: Path,
        skill_md: Path,
        category: str,
        created_by: int,
        force_update: bool
    ) -> str:
        """
        同步单个技能

        Returns:
            "created", "updated", or "skipped"
        """
        # 读取技能文件
        content = skill_md.read_text(encoding="utf-8")

        # 解析 YAML front matter
        meta = {}
        skill_content = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    meta = yaml.safe_load(parts[1]) or {}
                    skill_content = parts[2].strip()
                except:
                    pass

        # 检查技能是否已存在
        skill_name = skill_path.name
        existing_skill = db.query(Skill).filter(Skill.name == skill_name).first()

        if existing_skill:
            if not force_update:
                return "skipped"

            # 更新现有技能
            existing_skill.content = skill_content
            existing_skill.meta = meta if meta else None  # Store dict directly, not JSON string!
            existing_skill.category = category
            existing_skill.updated_at = datetime.utcnow()

            db.commit()
            return "updated"

        else:
            # 创建新技能
            skill = Skill(
                name=skill_name,
                category=category,
                content=skill_content,
                meta=meta if meta else None,  # Store dict directly, not JSON string!
                is_active=True,
                version="1.0.0",
                created_by=created_by,
                sharing_scope="public",
                is_official=True,
                usage_count=0,
                rating=None,
                rating_count=0,
                documentation=None
            )

            db.add(skill)
            db.commit()
            return "created"

    def _merge_stats(self, total: Dict, partial: Dict) -> None:
        """合并统计信息"""
        total["total"] += partial.get("total", 0)
        total["created"] += partial.get("created", 0)
        total["updated"] += partial.get("updated", 0)
        total["skipped"] += partial.get("skipped", 0)
        total["failed"] += partial.get("failed", 0)
        total["errors"].extend(partial.get("errors", []))


def get_framework_path() -> Path:
    """获取 Framework 路径"""
    # 从当前文件路径推导
    current_file = Path(__file__).resolve()
    backend_path = current_file.parent.parent  # backend/
    project_root = backend_path.parent.parent  # packages/
    return project_root / "framework"
