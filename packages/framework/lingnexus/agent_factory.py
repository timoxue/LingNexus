"""
Agent 工厂类
用于创建配置好的 ReActAgent 实例

注意：
- ReActAgent 需要直接传入模型实例，不支持 model_config_name
- agentscope.init() 主要用于全局配置（日志、Studio等），不用于模型配置
- 因此我们采用直接实例化模型的方式
"""

from typing import List, Optional
from pathlib import Path
from agentscope.agent import ReActAgent
from agentscope.model import ChatModelBase
from agentscope.formatter import FormatterBase
from agentscope.tool import Toolkit

from .config.model_config import create_model, get_formatter, ModelType
from .utils.skill_loader import SkillLoader


class AgentFactory:
    """创建配置好的 ReActAgent 实例"""
    
    def __init__(self, skills_base_dir: str | Path = "skills"):
        """
        初始化 Agent 工厂
        
        Args:
            skills_base_dir: Skills 基础目录路径
        """
        self.skill_loader = SkillLoader(skills_base_dir)
    
    def create_docx_agent(
        self,
        model_type: ModelType | str = ModelType.QWEN,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = 2048,
        additional_tools: Optional[List] = None,
        system_prompt: Optional[str] = None,
    ) -> ReActAgent:
        """
        创建支持 docx 技能的 Agent
        
        Args:
            model_type: 模型类型（"qwen" 或 "deepseek"）
            model_name: 模型名称，如果不提供则使用默认值
            api_key: API Key
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            additional_tools: 额外的工具列表
            system_prompt: 自定义系统提示词，如果不提供则使用默认提示词
        
        Returns:
            配置好的 ReActAgent 实例
        
        Examples:
            >>> factory = AgentFactory()
            >>> agent = factory.create_docx_agent(model_type="qwen")
            >>> response = agent.call("请帮我创建一个新的 Word 文档")
        """
        # 1. 创建模型和 formatter
        model = create_model(
            model_type=model_type,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        formatter = get_formatter(model_type)
        
        # 2. 注册 docx 技能
        self.skill_loader.register_skill("docx", skill_type="external")
        
        # 3. 获取技能提示词
        skill_prompt = self.skill_loader.get_skill_prompt()
        
        # 4. 构建系统提示词
        if system_prompt is None:
            system_prompt = """你是一个专业的文档处理助手，擅长处理 Word 文档（.docx 文件）。

你可以帮助用户：
- 创建新的 Word 文档
- 编辑和修改现有文档
- 处理文档中的跟踪更改和评论
- 提取和分析文档内容
- 处理文档格式和样式

"""
        
        if skill_prompt:
            system_prompt += f"\n{skill_prompt}\n"
        
        system_prompt += """
请根据用户的需求，使用合适的技能和工具来处理文档任务。
如果用户需要创建或编辑文档，请参考 docx 技能的说明和脚本。
"""
        
        # 5. 准备 Toolkit（如果需要额外工具）
        toolkit = self.skill_loader.get_toolkit()
        if additional_tools:
            for tool in additional_tools:
                toolkit.register_tool(tool)
        
        # 6. 创建 Agent
        agent = ReActAgent(
            name="docx_assistant",
            sys_prompt=system_prompt,
            model=model,
            formatter=formatter,
            toolkit=toolkit,
        )
        
        return agent
    
    def create_multi_skill_agent(
        self,
        skills: List[str],
        model_type: ModelType | str = ModelType.QWEN,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = 2048,
        skill_type: str = "external",
        system_prompt: Optional[str] = None,
    ) -> ReActAgent:
        """
        创建支持多个技能的 Agent
        
        Args:
            skills: 要注册的技能名称列表，如 ["docx", "pdf", "pptx"]
            model_type: 模型类型
            model_name: 模型名称
            api_key: API Key
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            skill_type: 技能类型（"external" 或 "internal"）
            system_prompt: 自定义系统提示词
        
        Returns:
            配置好的 ReActAgent 实例
        """
        # 1. 创建模型和 formatter
        model = create_model(
            model_type=model_type,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        formatter = get_formatter(model_type)
        
        # 2. 注册所有技能
        self.skill_loader.register_skills(skills, skill_type=skill_type)
        
        # 3. 获取技能提示词
        skill_prompt = self.skill_loader.get_skill_prompt()
        
        # 4. 构建系统提示词
        if system_prompt is None:
            system_prompt = f"""你是一个多功能的 AI 助手，支持以下技能：{', '.join(skills)}。

"""
        
        if skill_prompt:
            system_prompt += f"\n{skill_prompt}\n"
        
        system_prompt += "\n请根据用户的需求，选择合适的技能来完成任务。"
        
        # 5. 创建 Agent
        agent = ReActAgent(
            name="multi_skill_assistant",
            sys_prompt=system_prompt,
            model=model,
            formatter=formatter,
            toolkit=self.skill_loader.get_toolkit(),
        )
        
        return agent
    
    def create_progressive_agent(
        self,
        model_type: ModelType | str = ModelType.QWEN,
        model_name: str = "qwen-max",  # 默认使用 qwen-max
        skill_type: str = "external",
        api_key: Optional[str] = None,
        temperature: float = 0.3,  # orchestrator 使用较低温度
        max_tokens: int = 4096,
        system_prompt: Optional[str] = None,
    ) -> ReActAgent:
        """
        创建支持渐进式披露的 Agent（使用 qwen-max 作为 orchestrator）
        
        实现 Claude Skills 的渐进式披露机制：
        1. 阶段1：初始化时只加载所有 Skills 的元数据（~100 tokens/Skill）
        2. 阶段2：LLM 判断需要时，动态加载完整指令（~5k tokens）
        3. 阶段3：按需访问资源文件（scripts/, references/, assets/）
        
        Args:
            model_type: 模型类型（默认 QWEN）
            model_name: 模型名称（默认 "qwen-max"）
            skill_type: 技能类型（"external" 或 "internal"）
            api_key: API Key
            temperature: 温度参数（orchestrator 建议 0.3）
            max_tokens: 最大生成 token 数
            system_prompt: 自定义系统提示词
        
        Returns:
            配置好的 ReActAgent 实例
        
        Examples:
            >>> factory = AgentFactory()
            >>> agent = factory.create_progressive_agent(model_name="qwen-max")
            >>> response = await agent(Msg(name="user", content="创建一个 Word 文档"))
        """
        # 1. 创建模型（qwen-max）
        model = create_model(
            model_type=model_type,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        formatter = get_formatter(model_type)
        
        # 2. 加载所有 Skills 的元数据（阶段1）
        metadata_prompt = self.skill_loader.get_skills_metadata_prompt(skill_type)
        
        # 4. 构建系统提示词（只包含元数据）
        if system_prompt is None:
            system_prompt = """你是一个智能编排器（Orchestrator），负责协调和管理多个技能。

工作流程（三层渐进式披露）：
1. **阶段1 - 技能发现**：查看可用技能列表（元数据，~100 tokens/Skill）
2. **阶段2 - 技能选择**：根据用户需求，判断需要哪个技能
3. **阶段3 - 指令加载**：使用 `load_skill_instructions` 工具加载选定技能的完整指令（~5k tokens）
4. **阶段4 - 参考文档**：如果指令中引用了参考文档，使用 `load_skill_reference` 按需加载
5. **阶段5 - 资源访问**：通过 `get_skill_resource_path` 获取资源路径，访问 scripts/、assets/ 等
6. **阶段6 - 任务执行**：根据完整指令和参考文档规划并执行任务

重要原则：
- 初始时只看到技能的元数据（名称和描述），节省 tokens
- 只有在确定需要某个技能时，才加载其完整指令
- 如果指令中引用了参考文档（如 docx-js.md, ooxml.md），按需加载这些文档
- 一次只加载一个技能的完整指令，避免 token 浪费
- 根据任务的复杂度，可能需要加载多个技能和参考文档

"""
        
        # 添加元数据提示词
        if metadata_prompt:
            system_prompt += f"\n{metadata_prompt}\n"
        
        system_prompt += """
## 可用工具（渐进式披露）

### 阶段1：元数据层
- `list_available_skills()`: 列出所有可用技能的元数据

### 阶段2：指令层
- `load_skill_instructions(skill_name)`: 加载指定技能的完整指令（SKILL.md）

### 阶段3：资源层
- `load_skill_reference(skill_name, reference_file)`: 加载参考文档（如 docx-js.md, ooxml.md）
- `list_skill_resources(skill_name)`: 列出技能的所有资源（references/, assets/, scripts/）
- `get_skill_resource_path(skill_name, resource_type)`: 获取资源路径（用于文件系统访问）

### 特殊工具
- `check_and_fix_js(js_code)`: 检查和修复 JavaScript 代码
  - 检查 Node.js 版本和代码语法
  - 自动修复全角符号等常见问题
  - 验证代码可执行性
  - 返回执行命令供 `execute_shell_command` 使用
  - **使用场景**: 当需要执行 JavaScript 代码时，先使用此工具检查，然后使用 `execute_shell_command` 执行返回的命令

请根据用户需求，智能地选择和使用技能，按需加载指令和参考文档。
"""
        
        # 5. 创建 Toolkit 并注册渐进式加载工具
        toolkit = Toolkit()
        # 注册渐进式加载工具（从 SkillLoader 获取）
        progressive_tools = self.skill_loader.get_progressive_tools()
        for tool_func in progressive_tools:
            toolkit.register_tool_function(tool_func)
        # 注意：这里不预先注册技能，让 Agent 按需加载
        
        # 6. 创建 Agent
        agent = ReActAgent(
            name="progressive_orchestrator",
            sys_prompt=system_prompt,
            model=model,
            formatter=formatter,
            toolkit=toolkit,
        )
        
        return agent

