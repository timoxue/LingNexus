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

from ..config.model_config import create_model, get_formatter, ModelType
from ..utils.skill_loader import SkillLoader


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

