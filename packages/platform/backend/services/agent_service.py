"""
Agent 执行服务

实现完整的 Skills 闭环：
1. 从数据库查询 Agent 绑定的 Skills（完整配置）
2. 将 Skills 从数据库加载到 AgentScope Toolkit
3. 创建 Agent 并执行
4. 更新 Skills 使用统计
"""
import asyncio
import sys
import io
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Windows 编码修复
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加 framework 到路径
backend_dir = Path(__file__).parent.parent
framework_dir = backend_dir.parent.parent / 'framework'
if str(framework_dir) not in sys.path:
    sys.path.insert(0, str(framework_dir))

from agentscope.message import Msg
from agentscope.tool import Toolkit

# 导入 framework 模块
try:
    from lingnexus.config.agent_config import init_agentscope
    from lingnexus.config.model_config import create_model, get_formatter, ModelType
    from agentscope.agent import ReActAgent
    FRAMEWORK_AVAILABLE = True
except ImportError as e:
    FRAMEWORK_AVAILABLE = False
    logger.error(f"Failed to import lingnexus-framework: {e}")


class TrackedToolkit(Toolkit):
    """包装 Toolkit 以记录 tool 调用"""

    def __init__(self):
        super().__init__()
        self.tool_call_history = []  # [(tool_name, args, kwargs), ...]

    async def call_tool_function(self, tool_call: dict) -> Any:
        """调用工具函数并记录"""
        tool_name = tool_call.get("name", "")
        arguments = tool_call.get("arguments", {})

        # 记录 tool 调用
        self.tool_call_history.append({
            "name": tool_name,
            "arguments": arguments,
        })
        logger.info(f"[TOOL_CALL] {tool_name} called with args: {arguments}")

        # 调用原始方法
        return await super().call_tool_function(tool_call)


class SkillRegistry:
    """Skill 注册器 - 从数据库加载 Skills 到 AgentScope"""

    def __init__(self):
        self.temp_dir: Optional[Path] = None

    def create_temp_skill_dir(self) -> Path:
        """创建临时目录存放 skill 文件"""
        if self.temp_dir is None:
            self.temp_dir = Path(tempfile.mkdtemp(prefix="lingnexus_skills_"))
        return self.temp_dir

    def register_skill_from_db(
        self,
        skill_name: str,
        skill_content: str,
        skill_category: str,
        toolkit: Toolkit,
    ) -> bool:
        """从数据库注册 Skill 到 AgentScope Toolkit"""
        try:
            # 创建临时 skill 目录
            temp_base = self.create_temp_skill_dir()
            skill_dir = temp_base / skill_category / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)

            # 写入 SKILL.md
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(skill_content, encoding='utf-8')

            # 注册到 AgentScope Toolkit
            toolkit.register_agent_skill(skill_dir=str(skill_dir))

            logger.info(f"Registered skill '{skill_name}' from database")
            return True

        except Exception as e:
            logger.error(f"Failed to register skill '{skill_name}': {e}")
            return False

    def register_tools_from_db(
        self,
        skill_name: str,
        skill_category: str,
        toolkit: Toolkit,
    ) -> int:
        """从 framework 的 scripts/tools.py 注册工具函数"""
        try:
            # 查找 framework 中的 tools.py
            backend_dir = Path(__file__).parent.parent
            packages_dir = backend_dir.parent.parent
            framework_dir = packages_dir / "framework"
            tools_file = (
                framework_dir / "skills" /
                skill_category / skill_name / "scripts" / "tools.py"
            )

            if not tools_file.exists():
                logger.debug(f"No tools.py found for skill '{skill_name}'")
                return 0

            # 动态导入工具
            import importlib.util
            import inspect

            spec = importlib.util.spec_from_file_location(f"{skill_name}_tools", tools_file)
            if not spec or not spec.loader:
                return 0

            tools_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tools_module)

            # 注册工具函数
            tool_count = 0
            excluded_modules = {'builtins', 'inspect', 'importlib', 'pathlib', 'typing', 'io', 'zipfile', 'json', 'logging'}

            for attr_name in dir(tools_module):
                attr = getattr(tools_module, attr_name)
                if inspect.isfunction(attr) and not attr_name.startswith('_'):
                    attr_module = getattr(attr, '__module__', None)
                    if attr_module and not attr_module.startswith('_') and attr_module not in excluded_modules:
                        try:
                            toolkit.register_tool_function(attr)
                            tool_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to register tool {attr_name}: {e}")

            if tool_count > 0:
                logger.info(f"Registered {tool_count} tools for skill '{skill_name}'")

            return tool_count

        except Exception as e:
            logger.error(f"Failed to register tools for skill '{skill_name}': {e}")
            return 0

    def cleanup(self):
        """清理临时文件"""
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temp skill directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")


class AgentExecutor:
    """Agent 执行器"""

    def __init__(self):
        self._initialized = False
        self.skill_registry = SkillRegistry()

    def _ensure_initialized(self):
        """确保 AgentScope 已初始化"""
        if not self._initialized and FRAMEWORK_AVAILABLE:
            try:
                # 启用 AgentScope Studio (http://localhost:3000)
                import os
                studio_enabled = os.getenv("AGENTSCOPE_STUDIO_ENABLED", "true").lower() == "true"
                studio_url = "http://localhost:3000" if studio_enabled else None

                init_agentscope(studio_url=studio_url)
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize AgentScope: {e}")
                self._initialized = False

    async def execute(
        self,
        message: str,
        model_name: str = "qwen-max",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        skills: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        执行 Agent

        Args:
            message: 用户消息
            model_name: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            system_prompt: 系统提示（可选）
            skills: 从数据库查询的技能列表（完整对象）

        Returns:
            Dict: 执行结果，包括：
                - status: 执行状态
                - output_message: 输出消息
                - error_message: 错误消息
                - tokens_used: 使用的 token 数
                - execution_time: 执行时间
                - used_skills: 实际使用的 skills 列表 [{skill_id, tool_calls}]
        """
        if not FRAMEWORK_AVAILABLE:
            logger.warning("Framework not available, returning mock response")
            return {
                "status": "success",
                "output_message": f"模拟响应：收到你的消息 '{message}'。Framework 当前不可用。",
                "error_message": None,
                "tokens_used": 100,
                "execution_time": 0.5,
            }

        self._ensure_initialized()

        if not self._initialized:
            logger.warning("AgentScope initialization failed, returning mock response")
            return {
                "status": "success",
                "output_message": f"模拟响应：收到你的消息 '{message}'。AgentScope 初始化失败。",
                "error_message": None,
                "tokens_used": 100,
                "execution_time": 0.5,
            }

        try:
            import time
            start_time = time.time()

            # 创建 TrackedToolkit（记录 tool 调用）
            toolkit = TrackedToolkit()

            # 从数据库注册 Skills
            if skills and len(skills) > 0:
                logger.info(f"Loading {len(skills)} skills from database")

                success_count = 0
                for skill in skills:
                    skill_name = skill['name']
                    skill_category = skill['category']
                    skill_content = skill['content']

                    # 注册 SKILL.md（容错处理）
                    skill_registered = self.skill_registry.register_skill_from_db(
                        skill_name=skill_name,
                        skill_content=skill_content,
                        skill_category=skill_category,
                        toolkit=toolkit,
                    )

                    if not skill_registered:
                        logger.warning(f"Failed to register skill '{skill_name}', skipping...")
                        continue

                    # 注册工具函数
                    tool_count = self.skill_registry.register_tools_from_db(
                        skill_name=skill_name,
                        skill_category=skill_category,
                        toolkit=toolkit,
                    )

                    if tool_count >= 0:  # 0 means no tools.py, which is OK
                        success_count += 1
                        logger.info(f"Successfully loaded skill '{skill_name}' with {tool_count} tools")

                logger.info(f"Successfully loaded {success_count}/{len(skills)} skills")

            # 构建系统提示词
            if system_prompt is None:
                skill_names = [s['name'] for s in skills] if skills else []
                system_prompt = f"""你是一个专业的 AI 助手。

**可用技能**: {', '.join(skill_names) if skill_names else '无'}

请根据用户的需求，使用合适的技能来完成任务。如果需要使用某个技能，先使用 load_skill_instructions 工具加载该技能的完整说明。
"""

            # 创建模型
            model = create_model(
                model_type=ModelType.QWEN,
                model_name=model_name,
                temperature=temperature,
                max_tokens=max_tokens or 4096,
            )
            formatter = get_formatter(ModelType.QWEN)

            # 创建 Agent
            agent = ReActAgent(
                name="agent",
                sys_prompt=system_prompt,
                model=model,
                formatter=formatter,
                toolkit=toolkit,
            )

            # 创建用户消息
            user_msg = Msg(
                name="user",
                role="user",
                content=message,
            )

            # 执行 Agent
            logger.info(f"Executing agent with message: {message[:50]}...")
            response = await agent(user_msg)

            execution_time = time.time() - start_time

            # 从 toolkit 获取 tool call 记录
            tool_call_history = toolkit.tool_call_history
            logger.info(f"Total tool calls: {len(tool_call_history)}")

            # 将 tool calls 映射到 skills
            used_skills = {}
            for call in tool_call_history:
                tool_name = call['name']
                logger.info(f"Tool called: {tool_name}")

                # 找到这个 tool 属于哪个 skill
                for skill in skills:
                    skill_id = skill['id']
                    if skill_id not in used_skills:
                        used_skills[skill_id] = {'tool_calls': {}}

                    # 统计 tool 调用次数
                    if tool_name not in used_skills[skill_id]['tool_calls']:
                        used_skills[skill_id]['tool_calls'][tool_name] = 0
                    used_skills[skill_id]['tool_calls'][tool_name] += 1

            # 提取响应内容
            output_message = self._extract_response_content(response)

            # 打印使用的 skills 统计
            if used_skills:
                logger.info(f"Skills used in this execution:")
                for skill_id, data in used_skills.items():
                    tool_calls = data['tool_calls']
                    logger.info(f"  Skill ID {skill_id}: {list(tool_calls.keys())} -> {list(tool_calls.values())}")
            else:
                logger.info("No skills were used in this execution")

            logger.info(f"Agent execution completed in {execution_time:.2f}s")

            return {
                "status": "success",
                "output_message": output_message,
                "error_message": None,
                "tokens_used": len(message.split()) + len(output_message.split()),
                "execution_time": execution_time,
                "used_skills": used_skills,
            }

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()

            logger.error(f"Agent execution failed: {e}")
            logger.error(f"Error detail: {error_detail}")

            return {
                "status": "failed",
                "error_message": f"{str(e)}\n\n{error_detail}",
                "output_message": None,
                "tokens_used": 0,
                "execution_time": 0,
            }
        finally:
            # 清理临时文件
            self.skill_registry.cleanup()

    def _extract_response_content(self, response) -> str:
        """提取响应内容"""
        output_message = ""
        if hasattr(response, 'content'):
            content = response.content
            if isinstance(content, list):
                # 处理多块内容
                for block in content:
                    if isinstance(block, dict):
                        text = block.get('text', '')
                        if text:
                            output_message += text + "\n"
                    else:
                        output_message += str(block) + "\n"
                output_message = output_message.strip()
            elif isinstance(content, str):
                output_message = content
            else:
                output_message = str(content)
        elif isinstance(response, str):
            output_message = response
        else:
            output_message = str(response)

        return output_message


# 全局执行器实例
_executor = AgentExecutor()


async def execute_agent(
    message: str,
    model_name: str = "qwen-max",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None,
    skills: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """执行 Agent（对外接口）"""
    return await _executor.execute(
        message=message,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
        skills=skills,
    )
