from typing import Any, Dict, List, Optional

import httpx

from config.settings import settings
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


class LLMManager:
    """大模型统一管理。
    
    支持从 api_keys.yaml 或 model_config.yaml 加载配置。
    优先使用 api_keys.yaml 中的配置，如果不存在则回退到 model_config.yaml。
    """

    def __init__(self) -> None:
        self._api_keys = settings.api_keys
        self._model_config = settings.llm_model_config
        self._default_model_name = self._model_config.default_llm
        self._client = httpx.AsyncClient(timeout=60.0)

    def _get_api_key_config(self, provider: str) -> Optional[Dict[str, Any]]:
        """从 api_keys.yaml 中获取指定 provider 的配置。"""
        provider_map = {
            "deepseek": self._api_keys.deepseek,
            "qwen": self._api_keys.qwen,
            "gemini": self._api_keys.gemini,
            "openai": self._api_keys.openai,
        }
        return provider_map.get(provider)

    def get_model_settings(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """获取模型配置，优先使用 api_keys.yaml。"""
        name = model_name or self._default_model_name
        if not name:
            raise ValueError("No default LLM configured, and model_name is None")

        # 先尝试从 api_keys.yaml 获取配置
        api_key_cfg = self._get_api_key_config(name)
        if api_key_cfg and api_key_cfg.get("api_key"):
            return {
                "api_base": api_key_cfg.get("base_url", ""),
                "model_name": api_key_cfg.get("model", name),
                "api_key": api_key_cfg.get("api_key"),
            }

        # 回退到 model_config.yaml
        model_cfg = self._model_config.models.get(name)
        if not model_cfg:
            raise ValueError(f"Model '{name}' not found in api_keys.yaml or model_config.yaml")

        return model_cfg

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model_name: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        """统一聊天接口。
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "xxx"}, ...]
            model_name: 模型名称（deepseek/qwen/gemini/openai 或 model_config.yaml 中的自定义名称）
            temperature: 温度参数
            max_tokens: 最大 token 数
        
        Returns:
            模型返回的文本内容
        """

        model_cfg = self.get_model_settings(model_name)
        api_base = model_cfg.get("api_base") or model_cfg.get("base_url")
        model = model_cfg.get("model_name") or model_cfg.get("model")
        
        # 优先使用 api_keys.yaml 中的 api_key
        api_key = model_cfg.get("api_key")
        
        # 如果 api_keys.yaml 没有，尝试从环境变量读取
        if not api_key:
            api_key_name = model_cfg.get("api_key_env", "OPENAI_API_KEY")
            api_key = getattr(settings, api_key_name.lower(), None) or settings.openai_api_key

        if not api_base or not model:
            raise ValueError(f"Model config for '{model_name or self._default_model_name}' is incomplete")
        
        if not api_key:
            raise ValueError(f"API key for '{model_name or self._default_model_name}' is not set")

        # 判断是否为 Gemini 模型（需要特殊处理）
        provider_name = model_name or self._default_model_name
        is_gemini = provider_name == "gemini" or "gemini" in model.lower()
        
        if is_gemini:
            # Gemini API 特殊处理
            return await self._call_gemini(api_base, model, api_key, messages, temperature, max_tokens)
        else:
            # OpenAI 兼容 API（DeepSeek, Qwen, OpenAI）
            return await self._call_openai_compatible(api_base, model, api_key, messages, temperature, max_tokens, provider_name)

    async def _call_openai_compatible(
        self,
        api_base: str,
        model: str,
        api_key: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
        provider_name: str,
    ) -> str:
        """调用 OpenAI 兼容格式的 API（DeepSeek, Qwen, OpenAI）。"""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        logger.info(
            "Calling LLM (OpenAI-compatible)",
            extra={
                "provider": provider_name,
                "model": model,
                "temperature": temperature,
            },
        )

        url = f"{api_base.rstrip('/')}/v1/chat/completions"
        resp = await self._client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

        content = data["choices"][0]["message"]["content"]
        return content

    async def _call_gemini(
        self,
        api_base: str,
        model: str,
        api_key: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: Optional[int],
    ) -> str:
        """调用 Google Gemini API（特殊格式）。"""
        
        # Gemini API 使用 URL 参数传递 API Key
        url = f"{api_base.rstrip('/')}/models/{model}:generateContent?key={api_key}"
        
        # 转换消息格式：OpenAI 格式 -> Gemini 格式
        gemini_contents = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            gemini_contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        payload: Dict[str, Any] = {
            "contents": gemini_contents,
            "generationConfig": {
                "temperature": temperature,
            }
        }
        
        if max_tokens is not None:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens

        logger.info(
            "Calling LLM (Gemini)",
            extra={
                "provider": "gemini",
                "model": model,
                "temperature": temperature,
            },
        )

        headers = {"Content-Type": "application/json"}
        resp = await self._client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

        # 解析 Gemini 响应格式
        if "candidates" in data and len(data["candidates"]) > 0:
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            return content
        else:
            raise ValueError(f"Gemini API returned unexpected response: {data}")


llm_manager = LLMManager()
