from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings

# 项目根目录（假设 settings.py 在 config/ 下）
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class ModelConfig(BaseSettings):
    """对应 config/model_config.yaml 的结构。"""

    default_llm: Optional[str] = None
    models: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class APIKeysConfig(BaseSettings):
    """对应 config/api_keys.yaml 的结构。"""

    deepseek: Dict[str, Any] = Field(default_factory=dict)
    qwen: Dict[str, Any] = Field(default_factory=dict)
    gemini: Dict[str, Any] = Field(default_factory=dict)
    openai: Dict[str, Any] = Field(default_factory=dict)
    agentscope: Dict[str, Any] = Field(default_factory=dict)


class AgentScopeConfig(BaseSettings):
    """对应 config/agentscope_config.yaml。"""

    default_agent: Optional[str] = None
    agents: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class ServiceConfig(BaseSettings):
    """对应 config/service_config.yaml。"""

    intelligence_service_port: int = 8001
    bd_service_port: int = 8002
    rd_service_port: int = 8003

    # 存储后端选择（模式 B/C）
    es_backend: str = "local_file"      # local_file | remote_es
    vector_backend: str = "chroma"      # none | chroma | milvus

    # 远程服务配置（模式 C）
    es_url: Optional[str] = None
    vector_url: Optional[str] = None
    rdb_url: Optional[str] = None
    redis_url: Optional[str] = None


class Settings(BaseSettings):
    """全局配置入口。"""

    # 基础环境变量
    environment: str = Field(default="dev", validation_alias="ENVIRONMENT")
    openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")

    # 嵌套配置（从 YAML 加载）
    api_keys: APIKeysConfig = Field(default_factory=APIKeysConfig)
    model_config: ModelConfig = Field(default_factory=ModelConfig)
    agentscope_config: AgentScopeConfig = Field(default_factory=AgentScopeConfig)
    service_config: ServiceConfig = Field(default_factory=ServiceConfig)

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @classmethod
    def load(cls) -> "Settings":
        """工厂方法：加载 env 与 YAML 配置。"""

        # 先加载基础 env
        settings = cls()

        # 加载 YAML
        api_keys_yaml = load_yaml(CONFIG_DIR / "api_keys.yaml")
        model_yaml = load_yaml(CONFIG_DIR / "model_config.yaml")
        agentscope_yaml = load_yaml(CONFIG_DIR / "agentscope_config.yaml")
        service_yaml = load_yaml(CONFIG_DIR / "service_config.yaml")

        # 合并到嵌套配置（允许环境变量覆盖 YAML）
        settings.api_keys = APIKeysConfig(**api_keys_yaml)
        settings.model_config = ModelConfig(**model_yaml, _env_prefix="MODEL_")
        settings.agentscope_config = AgentScopeConfig(**agentscope_yaml, _env_prefix="AGENT_")
        settings.service_config = ServiceConfig(**service_yaml, _env_prefix="SERVICE_")

        return settings


# 对外暴露一个全局单例
settings = Settings.load()
