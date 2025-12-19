"""
Prompt 统一管理器

功能：
1. 从 YAML 文件加载 Prompt 配置
2. 根据 service + key 渲染 Prompt 模板
3. 支持版本管理和元数据查询
4. 提供日志记录以便追踪 Prompt 使用情况
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

# Prompt 文件所在目录
BASE_DIR = Path(__file__).resolve().parent
PROMPT_DIR = BASE_DIR


class PromptManager:
    """Prompt 统一管理器。
    
    使用示例：
        from shared.prompts.manager import prompt_manager
        
        # 获取渲染后的 Prompt
        text = prompt_manager.render(
            service="intelligence",
            key="intelligence_summary_v1",
            query="某药物的临床进展",
            context="相关背景信息..."
        )
        
        # 获取 Prompt 元数据
        meta = prompt_manager.get_metadata("intelligence", "intelligence_summary_v1")
        print(f"推荐模型: {meta['recommended_model']}")
    """

    def __init__(self) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._loaded_services: List[str] = []
        self._load_all()

    def _load_yaml(self, service_name: str) -> Dict[str, Any]:
        """加载指定服务的 YAML 配置文件。"""
        yaml_path = PROMPT_DIR / f"{service_name}.yaml"
        
        if not yaml_path.exists():
            logger.warning(
                "Prompt config file not found",
                extra={"service": service_name, "path": str(yaml_path)}
            )
            return {}
        
        try:
            with yaml_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            logger.info(
                "Prompt config loaded",
                extra={"service": service_name, "prompt_count": len(data)}
            )
            return data
        except Exception as e:
            logger.error(
                "Failed to load prompt config",
                extra={"service": service_name, "error": str(e)},
                exc_info=True
            )
            return {}

    def _load_all(self) -> None:
        """加载所有已知服务的 Prompt 配置。"""
        services = ["intelligence", "bd", "rd"]
        
        for service in services:
            self._cache[service] = self._load_yaml(service)
            self._loaded_services.append(service)
        
        logger.info(
            "All prompt configs loaded",
            extra={"services": self._loaded_services}
        )

    def reload(self, service: Optional[str] = None) -> None:
        """重新加载配置（用于热更新 Prompt）。
        
        Args:
            service: 指定服务名，如果为 None 则重载所有服务
        """
        if service:
            self._cache[service] = self._load_yaml(service)
            logger.info("Prompt config reloaded", extra={"service": service})
        else:
            self._load_all()
            logger.info("All prompt configs reloaded")

    def get_prompt_config(self, service: str, key: str) -> Dict[str, Any]:
        """获取完整的 Prompt 配置（包括元数据）。
        
        Args:
            service: 服务名（intelligence | bd | rd）
            key: Prompt key（如 intelligence_summary_v1）
            
        Returns:
            包含 description, version, template 等字段的字典
            
        Raises:
            KeyError: 如果服务或 key 不存在
        """
        if service not in self._cache:
            raise KeyError(f"Service '{service}' not found in prompt manager")
        
        prompts = self._cache[service]
        if key not in prompts:
            available_keys = list(prompts.keys())
            raise KeyError(
                f"Prompt key '{key}' not found in service '{service}'. "
                f"Available keys: {available_keys}"
            )
        
        return prompts[key]

    def get_metadata(self, service: str, key: str) -> Dict[str, Any]:
        """获取 Prompt 的元数据（不包括 template）。"""
        config = self.get_prompt_config(service, key)
        return {
            "description": config.get("description", ""),
            "version": config.get("version", 1),
            "recommended_model": config.get("recommended_model", "deepseek"),
            "locale": config.get("locale", "zh-CN"),
        }

    def render(self, service: str, key: str, **kwargs: Any) -> str:
        """渲染 Prompt 模板，填充变量。
        
        Args:
            service: 服务名
            key: Prompt key
            **kwargs: 模板中的变量（如 query, context 等）
            
        Returns:
            渲染后的 Prompt 文本
            
        Raises:
            KeyError: 如果服务/key 不存在，或缺少必需的模板变量
        """
        config = self.get_prompt_config(service, key)
        template: str = config.get("template", "")
        
        if not template:
            raise ValueError(f"Prompt '{service}.{key}' has no template")
        
        try:
            rendered = template.format(**kwargs)
            
            logger.info(
                "Prompt rendered",
                extra={
                    "service": service,
                    "prompt_key": key,
                    "version": config.get("version", 1),
                    "variables": list(kwargs.keys()),
                }
            )
            
            return rendered
        except KeyError as e:
            raise KeyError(
                f"Missing required variable {e} for prompt '{service}.{key}'"
            ) from e

    def list_prompts(self, service: str) -> List[Dict[str, Any]]:
        """列出指定服务的所有 Prompt 及其元数据。
        
        Args:
            service: 服务名
            
        Returns:
            包含所有 Prompt 元数据的列表
        """
        if service not in self._cache:
            return []
        
        prompts = self._cache[service]
        result = []
        
        for key, config in prompts.items():
            result.append({
                "key": key,
                "description": config.get("description", ""),
                "version": config.get("version", 1),
                "recommended_model": config.get("recommended_model", "deepseek"),
                "locale": config.get("locale", "zh-CN"),
            })
        
        return result

    def get_recommended_model(self, service: str, key: str) -> str:
        """获取 Prompt 推荐使用的模型。"""
        metadata = self.get_metadata(service, key)
        return metadata.get("recommended_model", "deepseek")


# 全局单例
prompt_manager = PromptManager()
