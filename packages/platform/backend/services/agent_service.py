"""
Agent 执行服务

架构说明：
==================
Backend 查询 Agent 绑定的技能列表，传递给 Framework。
Framework 使用 create_multi_skill_agent() 只加载这些技能。
Agent 通过 tools (load_skill_instructions) 动态加载技能指令。

优势：
- Agent 只能看到绑定的技能，避免幻觉
- 按需加载技能指令，节省 tokens
- 参考 AgentScope 的设计模式
"""
import asyncio
import sys
import io
from typing import Optional, Dict, Any, List

# Windows 编码修复
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from agentscope.message import Msg

# 导入 framework 模块（通过 UV workspace 直接导入）
try:
    from lingnexus.config import init_agentscope
    from lingnexus.agent_factory import AgentFactory
    FRAMEWORK_AVAILABLE = True
    print("[INFO] lingnexus-framework imported successfully")
except ImportError as e:
    FRAMEWORK_AVAILABLE = False
    print(f"[ERROR] Failed to import lingnexus-framework: {e}")
    print(f"[ERROR] Make sure 'lingnexus-framework' is installed via: uv sync")


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
        skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        执行 Agent

        Args:
            message: 用户消息
            model_name: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            system_prompt: 系统提示（可选）
            skills: 绑定的技能列表（可选）

        Returns:
            Dict: 执行结果
        """
        if not FRAMEWORK_AVAILABLE:
            # Framework 不可用时的模拟响应
            print("[WARNING] lingnexus-framework is not available, returning mock response")
            return {
                "status": "success",
                "output_message": f"模拟响应：收到你的消息 '{message}'。Framework 当前不可用，请确保已正确安装和配置 lingnexus-framework。",
                "error_message": None,
                "tokens_used": 100,
                "execution_time": 0.5,
            }

        self._ensure_initialized()

        if not self._initialized:
            print("[WARNING] AgentScope initialization failed, returning mock response")
            return {
                "status": "success",
                "output_message": f"模拟响应：收到你的消息 '{message}'。AgentScope 初始化失败，请检查 API key 配置。",
                "error_message": None,
                "tokens_used": 100,
                "execution_time": 0.5,
            }

        try:
            import time
            start_time = time.time()

            # 使用 AgentFactory 创建 Agent
            factory = AgentFactory()

            # 如果指定了技能列表，使用 create_multi_skill_agent
            if skills and len(skills) > 0:
                print(f"[DEBUG] Creating multi-skill agent with: {skills}")
                agent = factory.create_multi_skill_agent(
                    skills=skills,
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens or 4096,
                    skill_type="external",  # 默认从 external 加载
                    system_prompt=system_prompt,
                )
            else:
                # 没有指定技能，使用 progressive agent（加载所有技能）
                print(f"[DEBUG] No skills specified, using progressive agent")
                from lingnexus import create_progressive_agent
                agent = create_progressive_agent(
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens or 4096,
                )

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
                "status": "failed",
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
    skills: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    执行 Agent 的便捷函数

    Args:
        message: 用户消息
        model_name: 模型名称
        temperature: 温度参数
        max_tokens: 最大 token 数
        system_prompt: 系统提示
        skills: 要使用的技能列表

    Returns:
        Dict: 执行结果
    """
    return await _executor.execute(
        message=message,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
        skills=skills,
    )
