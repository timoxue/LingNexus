"""
应用配置

支持环境变量和 .env 文件配置
"""
import os
from pathlib import Path
from typing import List


# ==================== 基础路径配置 ====================

# 项目根目录（自动检测，使用绝对路径）
# config.py 位于 packages/platform/backend/core/config.py
# 需要向上 5 级到达项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent

# 后端目录
BACKEND_DIR = PROJECT_ROOT / "packages" / "platform" / "backend"


# ==================== 文件存储配置 ====================

# 文件存储基础目录（可通过环境变量覆盖）
ARTIFACTS_DIR = Path(os.getenv(
    "ARTIFACTS_DIR",
    str(BACKEND_DIR / "artifacts")
)).resolve()  # 确保是绝对路径

# 用户上传文件目录
USER_FILES_DIR = ARTIFACTS_DIR / "user_files"

# Agent 生成文件目录
AGENT_ARTIFACTS_DIR = ARTIFACTS_DIR / "agent_artifacts"

# 临时文件目录
TEMP_DIR = ARTIFACTS_DIR / "temp"


# ==================== 文件上传限制 ====================

# 允许的文件扩展名
ALLOWED_FILE_EXTENSIONS: List[str] = [
    # Office 文档
    'docx', 'pdf', 'xlsx', 'pptx',
    # 图片
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp',
    # 文本
    'txt', 'md', 'json', 'csv', 'xml',
    # 压缩文件
    'zip', 'rar', '7z', 'tar', 'gz',
]

# 最大文件大小（字节），默认 50MB
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))

# 文件 MIME 类型白名单（可选，空列表表示不限制）
ALLOWED_MIME_TYPES: List[str] = []  # 例如 ['application/pdf', 'image/jpeg']


# ==================== Agent 执行配置 ====================

# Agent 执行工作目录（默认使用系统临时目录）
AGENT_WORK_DIR = Path(os.getenv(
    "AGENT_WORK_DIR",
    str(Path(os.getenv("TEMP", "/tmp")) / "agent_workspace")
)).resolve()  # 确保是绝对路径

# 是否保留 Agent 执行工作目录（调试用）
PRESERVE_AGENT_WORK_DIR = os.getenv("PRESERVE_AGENT_WORK_DIR", "false").lower() == "true"


# ==================== 数据库配置 ====================

# 数据库文件路径
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BACKEND_DIR / 'lingnexus.db'}"
)


# ==================== 初始化函数 ====================

def ensure_directories():
    """确保所有必要的目录存在"""
    directories = [
        ARTIFACTS_DIR,
        USER_FILES_DIR,
        AGENT_ARTIFACTS_DIR,
        TEMP_DIR,
        AGENT_WORK_DIR,
    ]

    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Warning: Failed to create directory {directory}: {e}")


def get_config_summary() -> dict:
    """获取配置摘要（用于调试）"""
    return {
        "project_root": str(PROJECT_ROOT),
        "artifacts_dir": str(ARTIFACTS_DIR),
        "user_files_dir": str(USER_FILES_DIR),
        "agent_artifacts_dir": str(AGENT_ARTIFACTS_DIR),
        "temp_dir": str(TEMP_DIR),
        "agent_work_dir": str(AGENT_WORK_DIR),
        "max_file_size": MAX_FILE_SIZE,
        "allowed_extensions": ALLOWED_FILE_EXTENSIONS,
        "preserve_agent_work_dir": PRESERVE_AGENT_WORK_DIR,
    }


# 在导入时自动创建目录
ensure_directories()
