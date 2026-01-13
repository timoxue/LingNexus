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
import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
from core.config import AGENT_ARTIFACTS_DIR

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

# 导入文件服务
try:
    from .file_service import FileService
    FILE_SERVICE_AVAILABLE = True
except ImportError as e:
    FILE_SERVICE_AVAILABLE = False
    logger.error(f"Failed to import FileService: {e}")


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
        # 如果 temp_dir 为 None 或不存在，重新创建
        if self.temp_dir is None or not self.temp_dir.exists():
            self.temp_dir = Path(tempfile.mkdtemp(prefix="lingnexus_skills_"))
            logger.info(f"Created new temp skill directory: {self.temp_dir}")
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

    def scan_for_generated_files(self) -> List[Path]:
        """
        扫描临时目录查找生成的文件

        Returns:
            找到的文件路径列表
        """
        generated_files = []
        if not self.temp_dir or not self.temp_dir.exists():
            logger.warning(f"Temp directory not found: {self.temp_dir}")
            return generated_files

        try:
            logger.info(f"Scanning for generated files in: {self.temp_dir}")

            # 遍历临时目录，查找生成的文件
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = Path(root) / file

                    # 记录所有文件（用于调试）
                    logger.info(f"Scanning file: {file_path} (ext: {file_path.suffix})")

                    # 跳过 SKILL.md 和脚本文件
                    if file_path.name == "SKILL.md":
                        logger.info(f"Skipping SKILL.md: {file_path}")
                        continue
                    if file_path.suffix == '.py':
                        logger.info(f"Skipping Python file: {file_path}")
                        continue

                    # 只保留有意义的文件（文档、图片等）
                    if file_path.suffix in ['.docx', '.pdf', '.xlsx', '.pptx', '.png', '.jpg', '.jpeg', '.gif', '.txt']:
                        generated_files.append(file_path)
                        logger.info(f"✓ Found generated file: {file_path}")
                    else:
                        logger.info(f"✗ Skipping file with unsupported extension: {file_path}")

            logger.info(f"Found {len(generated_files)} generated files (supported types)")
        except Exception as e:
            logger.error(f"Error scanning for generated files: {e}")

        return generated_files


class AgentExecutor:
    """Agent 执行器"""

    def __init__(self):
        self._initialized = False
        self.skill_registry = SkillRegistry()
        self._generated_files: List[Path] = []  # 保存生成的文件路径

        # 初始化并保存 SkillLoader 实例（用于渐进式披露工具）
        if FRAMEWORK_AVAILABLE:
            try:
                from lingnexus.utils.skill_loader import SkillLoader
                framework_skills_dir = framework_dir / "skills"
                self.skill_loader = SkillLoader(skills_base_dir=framework_skills_dir)
                logger.info(f"SkillLoader initialized with skills directory: {framework_skills_dir}")
            except Exception as e:
                logger.warning(f"Failed to initialize SkillLoader: {e}")
                self.skill_loader = None
        else:
            self.skill_loader = None

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

            # 注册渐进式披露工具（load_skill_instructions 等）
            # 使用已保存的 SkillLoader 实例，确保工具可以访问其状态
            if self.skill_loader is not None:
                try:
                    progressive_tools = self.skill_loader.get_progressive_tools()
                    for tool_func in progressive_tools:
                        toolkit.register_tool_function(tool_func)
                    logger.info(f"Registered {len(progressive_tools)} progressive disclosure tools")
                except Exception as e:
                    logger.warning(f"Failed to register progressive tools: {e}")
            else:
                logger.warning("SkillLoader not initialized, skipping progressive tools registration")

            # 构建系统提示词
            if system_prompt is None:
                skill_names = [s['name'] for s in skills] if skills else []
                system_prompt = f"""你是一个专业的 AI 助手。

**可用技能**: {', '.join(skill_names) if skill_names else '无'}

**重要提示**:
1. 如果用户要求创建文档、文件等，请直接使用对应的工具函数，不要只是解释步骤
2. 例如：创建 docx 文档时，直接调用 create_new_docx(filename="xxx.docx")
3. 不要重复调用 load_skill_instructions，一次就足够了
4. 你的目标是完成任务，而不是只是描述如何完成任务

请根据用户的需求，直接使用合适的工具来完成任务。
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
                max_iters=10,  # 限制最大迭代次数，防止无限循环
            )

            # 创建用户消息
            user_msg = Msg(
                name="user",
                role="user",
                content=message,
            )

            # 创建 Agent 执行工作目录（持久化，不需要清理）
            import uuid
            execution_id_str = str(uuid.uuid4())[:8]  # 短 ID
            work_dir = AGENT_ARTIFACTS_DIR / "working" / execution_id_str
            work_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created agent work directory: {work_dir}")

            # 保存原始工作目录
            real_original_cwd = os.getcwd()

            # 切换到工作目录
            os.chdir(work_dir)

            try:
                # 执行 Agent（带超时保护）
                logger.info(f"Executing agent with message: {message[:50]}...")
                import asyncio
                response = await asyncio.wait_for(
                    agent(user_msg),
                    timeout=120.0  # 120秒超时
                )
            except asyncio.TimeoutError:
                logger.error("Agent execution timeout (120s)")
                raise Exception("Agent execution timeout: Agent did not respond within 120 seconds")
            finally:
                # 恢复原始工作目录
                os.chdir(real_original_cwd)

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
            # 扫描工作目录中生成的文件（已经在持久化目录中）
            self._generated_files = self._scan_work_directory(work_dir)
            logger.info(f"Found {len(self._generated_files)} generated files")

            # 清理技能临时目录（仅 SKILL.md 文件，不影响生成的文件）
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

    def _scan_work_directory(self, work_dir: Path) -> List[Path]:
        """
        扫描 Agent 工作目录查找生成的文件

        Args:
            work_dir: 工作目录路径

        Returns:
            找到的文件路径列表
        """
        generated_files = []

        if not work_dir or not work_dir.exists():
            logger.warning(f"Work directory not found: {work_dir}")
            return generated_files

        try:
            logger.info(f"Scanning work directory: {work_dir}")

            # 遍历工作目录，查找生成的文件
            for root, dirs, files in os.walk(work_dir):
                for file in files:
                    file_path = Path(root) / file

                    # 记录所有文件（用于调试）
                    logger.info(f"Scanning file: {file_path} (ext: {file_path.suffix})")

                    # 跳过 SKILL.md 和脚本文件
                    if file_path.name == "SKILL.md":
                        logger.info(f"Skipping SKILL.md: {file_path}")
                        continue
                    if file_path.suffix == '.py':
                        logger.info(f"Skipping Python file: {file_path}")
                        continue

                    # 只保留有意义的文件（文档、图片等）
                    if file_path.suffix in ['.docx', '.pdf', '.xlsx', '.pptx', '.png', '.jpg', '.jpeg', '.gif', '.txt']:
                        generated_files.append(file_path)
                        logger.info(f"✓ Found generated file: {file_path}")
                    else:
                        logger.info(f"✗ Skipping file with unsupported extension: {file_path}")

            logger.info(f"Found {len(generated_files)} generated files (supported types)")
        except Exception as e:
            logger.error(f"Error scanning work directory: {e}")

        return generated_files

    def capture_and_save_artifacts(
        self,
        agent_execution_id: int,
        db: Session,
    ) -> List[Dict[str, Any]]:
        """
        捕获并保存 Agent 执行生成的文件

        注意：此方法必须在 execute() 之后立即调用

        Args:
            agent_execution_id: Agent 执行 ID
            db: 数据库会话

        Returns:
            保存的文件信息列表
        """
        if not FILE_SERVICE_AVAILABLE:
            logger.warning("FileService not available, skipping artifact capture")
            return []

        # 使用在 execute() 中已经扫描的文件列表
        generated_files = self._generated_files
        if not generated_files:
            logger.info("No generated files found from execution")
            return []

        logger.info(f"Processing {len(generated_files)} generated files")

        artifacts = []
        for file_path in generated_files:
            try:
                # 文件已经在持久化目录中，直接移动到最终位置
                file_id = FileService.generate_file_id()
                file_type = FileService.get_file_extension(file_path.name)
                mime_type = FileService.get_mime_type(file_path.name)
                file_size = file_path.stat().st_size

                # 目标路径
                relative_path = f"agent_artifacts/{agent_execution_id}/{file_id}"
                dest_path = FileService.BASE_DIR / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # 移动文件
                shutil.move(str(file_path), str(dest_path))
                logger.info(f"Moved file from {file_path} to {dest_path}")

                # 创建数据库记录
                from ..db.models import AgentArtifact
                artifact = AgentArtifact(
                    agent_execution_id=agent_execution_id,
                    file_id=file_id,
                    filename=file_path.name,
                    file_type=file_type,
                    file_size=file_size,
                    mime_type=mime_type,
                    storage_path=relative_path,
                )

                db.add(artifact)
                db.commit()
                db.refresh(artifact)

                logger.info(f"Saved artifact: {artifact.file_id} - {artifact.filename}")
                artifacts.append({
                    "id": artifact.id,
                    "file_id": artifact.file_id,
                    "filename": artifact.filename,
                    "file_type": artifact.file_type,
                    "file_size": artifact.file_size,
                    "download_url": f"/api/v1/files/artifacts/{artifact.file_id}/download",
                    "preview_url": f"/api/v1/files/artifacts/{artifact.file_id}/preview",
                })

            except Exception as e:
                logger.error(f"Failed to save artifact {file_path}: {e}")
                db.rollback()

        logger.info(f"Captured and saved {len(artifacts)} artifacts")
        return artifacts


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
