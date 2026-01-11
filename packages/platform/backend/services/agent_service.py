"""
Agent 执行服务
连接到 lingnexus-framework 的 Agent
"""
import asyncio
import sys
import io
from typing import Optional, Dict, Any

# Windows 编码修复
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from agentscope.message import Msg

# 导入 framework 模块
try:
    from lingnexus.config import init_agentscope
    from lingnexus.agent import create_progressive_agent
    FRAMEWORK_AVAILABLE = True
except ImportError:
    FRAMEWORK_AVAILABLE = False


class AgentExecutor:
    """Agent 执行器"""

    def __init__(self):
        self._initialized = False

    def _ensure_initialized(self):
        """确保 AgentScope 已初始化"""
        if not self._initialized and FRAMEWORK_AVAILABLE:
            try:
                init_agentscope()
                self._initialized = True
            except Exception as e:
                print(f"Warning: Failed to initialize AgentScope: {e}")
                self._initialized = False

    async def execute(
        self,
        message: str,
        model_name: str = "qwen-max",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        执行 Agent

        Args:
            message: 用户消息
            model_name: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            system_prompt: 系统提示（可选）

        Returns:
            Dict: 执行结果
        """
        if not FRAMEWORK_AVAILABLE:
            return {
                "status": "error",
                "error_message": "lingnexus-framework is not available",
                "output_message": None,
                "tokens_used": 0,
                "execution_time": 0,
            }

        self._ensure_initialized()

        if not self._initialized:
            return {
                "status": "error",
                "error_message": "AgentScope initialization failed",
                "output_message": None,
                "tokens_used": 0,
                "execution_time": 0,
            }

        try:
            import time
            start_time = time.time()

            # 创建 Agent
            agent = create_progressive_agent(
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens or 4096,
            )

            # 如果有系统提示，设置到 Agent
            if system_prompt:
                agent.system_prompt = system_prompt

            # 创建用户消息
            user_msg = Msg(
                name="user",
                role="user",
                content=message,
            )

            # 执行 Agent
            response = await agent(user_msg)

            execution_time = time.time() - start_time

            # 提取响应内容
            output_message = ""
            if hasattr(response, 'content'):
                output_message = response.content
            elif isinstance(response, str):
                output_message = response
            elif isinstance(response, dict):
                output_message = str(response)
            else:
                output_message = str(response)

            # 估算 token 使用量（粗略估计）
            tokens_used = len(message.split()) + len(str(output_message).split())

            return {
                "status": "success",
                "output_message": output_message,
                "error_message": None,
                "tokens_used": tokens_used,
                "execution_time": execution_time,
            }

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()

            return {
                "status": "error",
                "error_message": f"{str(e)}\n\n{error_detail}",
                "output_message": None,
                "tokens_used": 0,
                "execution_time": 0,
            }


# 全局执行器实例
_executor = AgentExecutor()


async def execute_agent(
    message: str,
    model_name: str = "qwen-max",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    执行 Agent 的便捷函数

    Args:
        message: 用户消息
        model_name: 模型名称
        temperature: 温度参数
        max_tokens: 最大 token 数
        system_prompt: 系统提示

    Returns:
        Dict: 执行结果
    """
    return await _executor.execute(
        message=message,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
    )
