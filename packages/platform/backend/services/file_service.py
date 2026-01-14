"""
文件存储服务

处理文件上传、保存和元数据管理
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import UploadFile, HTTPException
import mimetypes

from core.config import (
    ARTIFACTS_DIR,
    USER_FILES_DIR,
    AGENT_ARTIFACTS_DIR,
    ALLOWED_FILE_EXTENSIONS,
    MAX_FILE_SIZE,
)


class FileService:
    """文件存储服务"""

    # 使用配置文件中的路径
    BASE_DIR = ARTIFACTS_DIR
    USER_FILES_DIR = USER_FILES_DIR
    AGENT_ARTIFACTS_DIR = AGENT_ARTIFACTS_DIR
    ALLOWED_EXTENSIONS = set(ALLOWED_FILE_EXTENSIONS)
    MAX_FILE_SIZE = MAX_FILE_SIZE

    @classmethod
    def ensure_directories(cls):
        """确保存储目录存在"""
        cls.BASE_DIR.mkdir(parents=True, exist_ok=True)
        cls.USER_FILES_DIR.mkdir(parents=True, exist_ok=True)
        cls.AGENT_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def generate_file_id(cls) -> str:
        """生成唯一文件 ID"""
        return f"f_{uuid.uuid4().hex[:16]}"

    @classmethod
    def get_mime_type(cls, filename: str) -> str:
        """获取 MIME 类型"""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or "application/octet-stream"

    @classmethod
    def get_file_extension(cls, filename: str) -> str:
        """获取文件扩展名"""
        return filename.split('.')[-1].lower() if '.' in filename else ''

    @classmethod
    async def save_upload_file(
        cls,
        file: UploadFile,
        user_id: int,
        folder_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        保存用户上传的文件

        Args:
            file: FastAPI UploadFile 对象
            user_id: 用户 ID
            folder_id: 文件夹 ID（可选）

        Returns:
            包含文件元数据的字典

        Raises:
            ValueError: 文件验证失败
        """
        # 确保目录存在
        cls.ensure_directories()

        # 验证文件
        validation_result = await cls._validate_file(file)
        if not validation_result["valid"]:
            raise ValueError(validation_result["error"])

        # 生成存储路径
        file_id = cls.generate_file_id()
        relative_path = f"user_files/{user_id}/{file_id[:2]}/{file_id}"
        full_path = cls.BASE_DIR / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存文件
        try:
            with open(full_path, "wb") as f:
                content = await file.read()
                f.write(content)

            file_size = len(content)

            return {
                "file_id": file_id,
                "storage_path": relative_path,
                "file_size": file_size,
                "mime_type": cls.get_mime_type(file.filename),
                "file_type": cls.get_file_extension(file.filename),
            }
        except Exception as e:
            # 清理失败的文件
            if full_path.exists():
                full_path.unlink()
            raise ValueError(f"Failed to save file: {str(e)}")

    @classmethod
    def save_agent_artifact(
        cls,
        source_path: Path,
        agent_execution_id: int
    ) -> Dict[str, Any]:
        """
        保存 Agent 生成的文件

        Args:
            source_path: 源文件路径
            agent_execution_id: Agent 执行 ID

        Returns:
            包含文件元数据的字典

        Raises:
            FileNotFoundError: 源文件不存在
            ValueError: 文件保存失败
        """
        # 确保目录存在
        cls.ensure_directories()

        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")

        # 生成存储路径
        file_id = cls.generate_file_id()
        relative_path = f"agent_artifacts/{agent_execution_id}/{file_id}"
        full_path = cls.BASE_DIR / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 复制文件
            shutil.copy(source_path, full_path)

            return {
                "file_id": file_id,
                "storage_path": relative_path,
                "file_size": source_path.stat().st_size,
                "mime_type": cls.get_mime_type(source_path.name),
                "file_type": cls.get_file_extension(source_path.name),
            }
        except Exception as e:
            # 清理失败的文件
            if full_path.exists():
                full_path.unlink()
            raise ValueError(f"Failed to save artifact: {str(e)}")

    @classmethod
    async def _validate_file(cls, file: UploadFile) -> Dict[str, Any]:
        """
        验证文件

        Args:
            file: FastAPI UploadFile 对象

        Returns:
            验证结果字典 {"valid": bool, "error": str}
        """
        # 检查文件名
        if not file.filename:
            return {"valid": False, "error": "Filename is required"}

        # 检查扩展名
        ext = cls.get_file_extension(file.filename)
        if ext not in cls.ALLOWED_EXTENSIONS:
            return {
                "valid": False,
                "error": f"File type '{ext}' is not allowed. Allowed types: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            }

        # 检查大小
        content = await file.read()
        if len(content) > cls.MAX_FILE_SIZE:
            return {
                "valid": False,
                "error": f"File size exceeds limit ({cls.MAX_FILE_SIZE / 1024 / 1024:.0f}MB)"
            }

        # 重置文件指针
        await file.seek(0)

        return {"valid": True, "error": None}

    @classmethod
    def get_file_path(cls, storage_path: str) -> Path:
        """
        获取文件的完整路径

        Args:
            storage_path: 相对存储路径

        Returns:
            文件的完整 Path 对象
        """
        full_path = cls.BASE_DIR / storage_path
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        return full_path

    @classmethod
    def delete_file(cls, storage_path: str) -> bool:
        """
        删除文件

        Args:
            storage_path: 相对存储路径

        Returns:
            是否成功删除
        """
        try:
            full_path = cls.BASE_DIR / storage_path
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception:
            return False

    @classmethod
    def get_file_size_formatted(cls, file_size: int) -> str:
        """
        格式化文件大小

        Args:
            file_size: 文件大小（字节）

        Returns:
            格式化后的文件大小字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if file_size < 1024.0:
                return f"{file_size:.1f} {unit}"
            file_size /= 1024.0
        return f"{file_size:.1f} TB"
