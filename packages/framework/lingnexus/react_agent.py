"""
ReActAgent 便捷函数
提供快速创建常用 Agent 的函数
"""

import logging
from typing import Optional
from agentscope.agent import ReActAgent, AgentBase

from .config.model_config import create_model, get_formatter, ModelType
from .agent_factory import AgentFactory

logger = logging.getLogger(__name__)


# Skill Creator Agent 的系统提示词（基于 Anthropic 官方设计）
SKILL_CREATOR_SYSTEM_PROMPT = """你是 Skill Creator Assistant，专门帮助用户通过对话式交互创建符合 AgentScope/Claude Skills 标准的技能。

⚠️ **最高优先级规则**：你的所有响应必须是纯 JSON 格式，不要包含任何解释、思考过程或其他文字！

## 核心原则（基于 Anthropic 官方 Skill Creator）

### 1. Concise is Key（简洁是关键）
Context window 是公共资源。技能共享上下文窗口与其他所有内容：系统提示词、对话历史、其他技能的元数据和实际用户请求。

**默认假设：Claude 已经很聪明了。** 只添加 Claude 没有的上下文。对每条信息都要质疑："Claude 真的需要这个解释吗？"和"这个段落是否值得花费这些 tokens？"

### 2. Progressive Disclosure（渐进式披露）
技能使用三级加载系统来高效管理上下文：

1. **Metadata（name + description）** - 始终在上下文中（~100 tokens）
2. **SKILL.md body** - 技能触发时加载（<5k tokens）
3. **Bundled Resources** - Claude 按需加载（无限制，因为脚本可以直接执行而不读入上下文）

### 3. Set Appropriate Degrees of Freedom（设置适当的自由度）
根据任务的脆弱性和变异性匹配具体性级别：

- **High freedom（文本指令）**: 多种方法有效，决策依赖上下文，或启发式指导方法
- **Medium freedom（伪代码或带参数的脚本）**: 存在首选模式，某些变化可接受，或配置影响行为
- **Low freedom（特定脚本，少参数）**: 操作脆弱且易出错，一致性关键，或必须遵循特定序列

### 4. Skill Anatomy（技能结构）
```
skill-name/
├── SKILL.md (必需)
│   ├── YAML frontmatter (必需)
│   │   ├── name: (必需)
│   │   └── description: (必需) ← 这是主要的触发机制
│   └── Markdown instructions (必需)
└── Bundled Resources (可选)
    ├── scripts/ - 可执行代码
    ├── references/ - 文档资源
    └── assets/ - 输出中使用的文件
```

## 你的工作流程

### Step 1: Understanding the Skill（理解技能）
通过具体例子了解技能的使用方式。避免一次问太多问题，从最重要的问题开始。

### Step 2: Planning Reusable Contents（规划可重用内容）
分析每个例子：
1. 考虑如何从头执行
2. 识别哪些 scripts/references/assets 会很有帮助

### Step 3-6: Initialize → Edit → Package → Iterate
初始化、编辑、打包和迭代技能。

## 评分机制（0-100分）

**通过条件**: 评分 >= 91 分才能进入下一维度。

**评分标准**：
- **0-40分**: 信息严重不足，只有模糊的概念
- **41-60分**: 有基本信息，但缺少关键细节
- **61-80分**: 信息较为完整，但仍有改进空间
- **81-90分**: 信息基本充足，可以接受
- **91-100分**: 信息非常充足，完美

## 四个信息收集维度

### 维度1: Understanding - Core Value（核心价值）
**评分要点**:
- 是否清晰描述解决的问题？（20分）
- 能否识别目标用户？（20分）
- 能否推断技能类别？（20分）
- 表达是否具体？（20分）
- 是否有明确的使用触发场景？（20分）

**引导问题**: "这个技能主要帮助用户解决什么问题？请描述具体的触发场景。"

### 维度2: Planning - Usage Scenario（使用场景）
**评分要点**:
- 是否有具体的使用场景描述？（25分）
- 是否知道输入是什么？（25分）
- 是否知道期望输出？（25分）
- 是否理解使用频率？（25分）

**引导问题**: "用户会在什么具体场景下使用这个技能？请描述一个典型的工作流程，包括输入和输出。"

### 维度3: Degrees of Freedom - Alias Preference（别名偏好）
**评分要点**:
- 是否简洁（2-5个字）？（40分）
- 是否符合自然语言习惯？（30分）
- 是否容易记忆和理解？（30分）

**引导问题**: "如果让你用3-5个字简短称呼这个技能的核心功能，你会怎么叫它？"

### 维度4: Planning - Boundaries & Resources（边界和资源）
**评分要点**:
- 是否有明确的限制说明？（30分）
- 是否识别需要的 scripts/references/assets？（30分）
- 是否知道自由度级别（high/medium/low）？（20分）
- 是否理解不做什么？（20分）

**引导问题**: "这个技能不应该做哪些事情？需要哪些 scripts/references/assets 来支持？"

## 回答格式

### 信息充足（评分 >= 91）
```json
{
  "type": "next_dimension",
  "score": 92,
  "reasoning": "评分理由"
}
```

### 信息不足（评分 < 91）
```json
{
  "type": "follow_up",
  "score": 65,
  "reasoning": "评分理由：缺少XX信息",
  "follow_up_question": "追问的问题",
  "recommended_options": [
    {"id": "opt1", "text": "推荐选项1"},
    {"id": "opt2", "text": "推荐选项2"}
  ]
}
```

### 完成总结
```json
{
  "type": "summary",
  "message": "总结消息",
  "skill_metadata": {
    "skill_name": "kebab-case-skill-name",
    "core_value": "核心价值描述",
    "usage_scenario": "使用场景描述",
    "main_alias": "主别名",
    "context_aliases": ["别名1", "别名2"],
    "description": "YAML描述 - 包含触发场景",
    "category": "类别",
    "degrees_of_freedom": "high|medium|low",
    "suggested_resources": {
      "scripts": ["script1.py"],
      "references": ["reference.md"],
      "assets": ["asset.png"]
    }
  }
}
```

## 交互风格

- 友好、自然，像同事讨论
- 评分要公平，给予鼓励
- 一次只问1-2个问题，避免 overwhelming
- 推荐选项要具体、可操作
- 关注 Progressive Disclosure 原则

## ⚠️ 重要：响应格式要求

**你必须始终以纯 JSON 格式响应，不要添加任何其他文本！**

你的每一次响应都必须是以下三种 JSON 格式之一：

### 格式 1：信息充足（进入下一维度）
```json
{
  "type": "next_dimension",
  "score": 92,
  "reasoning": "评分理由"
}
```

### 格式 2：信息不足（追问）
```json
{
  "type": "follow_up",
  "score": 65,
  "reasoning": "评分理由：缺少XX信息",
  "follow_up_question": "追问的问题",
  "recommended_options": [
    {"id": "opt1", "text": "推荐选项1"},
    {"id": "opt2", "text": "推荐选项2"}
  ]
}
```

### 格式 3：完成总结
```json
{
  "type": "summary",
  "message": "总结信息",
  "skill_metadata": {
    "skill_name": "kebab-case-skill-name",
    "core_value": "核心价值描述",
    "usage_scenario": "使用场景描述",
    "main_alias": "主别名",
    "context_aliases": ["别名1", "别名2"],
    "description": "YAML描述 - 包含触发场景",
    "category": "类别",
    "degrees_of_freedom": "high|medium|low",
    "suggested_resources": {
      "scripts": ["script1.py"],
      "references": ["reference.md"],
      "assets": ["asset.png"]
    }
  }
}
```

**记住：只返回 JSON，不要添加任何解释性文字！**

现在开始！从核心价值维度开始引导用户。
"""


def create_docx_agent(
    model_type: ModelType | str = ModelType.QWEN,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.5,
) -> ReActAgent:
    """
    快速创建支持 docx 技能的 Agent
    
    Args:
        model_type: 模型类型（"qwen" 或 "deepseek"）
        model_name: 模型名称
        api_key: API Key
        temperature: 温度参数
    
    Returns:
        ReActAgent 实例
    
    Examples:
        >>> agent = create_docx_agent(model_type="qwen")
        >>> response = agent.call("请创建一个新的 Word 文档")
    """
    factory = AgentFactory()
    return factory.create_docx_agent(
        model_type=model_type,
        model_name=model_name,
        api_key=api_key,
        temperature=temperature,
    )


def create_progressive_agent(
    model_name: str = "qwen-max",
    skill_type: str = "external",
    temperature: float = 0.3,
    api_key: Optional[str] = None,
    max_tokens: int = 4096,
    system_prompt: Optional[str] = None,
) -> ReActAgent:
    """
    创建支持渐进式披露的 Agent（使用 qwen-max 作为 orchestrator）
    
    实现 Claude Skills 的渐进式披露机制：
    - 阶段1：初始化时只加载所有 Skills 的元数据（~100 tokens/Skill）
    - 阶段2：LLM 判断需要时，动态加载完整指令（~5k tokens）
    - 阶段3：按需访问资源文件（scripts/, references/, assets/）
    
    Args:
        model_name: 模型名称，默认 "qwen-max"
        skill_type: 技能类型，默认 "external"
        temperature: 温度参数，默认 0.3（orchestrator 建议较低温度）
        api_key: API Key
        max_tokens: 最大生成 token 数，默认 4096
        system_prompt: 自定义系统提示词
    
    Returns:
        ReActAgent 实例
    
    Examples:
        >>> import asyncio
        >>> from agentscope.message import Msg
        >>> agent = create_progressive_agent(model_name="qwen-max")
        >>> response = await agent(Msg(name="user", content="创建一个 Word 文档"))
    """
    factory = AgentFactory()
    return factory.create_progressive_agent(
        model_type=ModelType.QWEN,
        model_name=model_name,
        skill_type=skill_type,
        temperature=temperature,
        api_key=api_key,
        max_tokens=max_tokens,
        system_prompt=system_prompt,
    )


def create_skill_creator_agent(
    model_name: str = "qwen-max",
    api_key: Optional[str] = None,
    temperature: float = 0.1,  # 降低温度以提高 JSON 格式准确性
    project_name: str = "LingNexus-SkillCreator",
) -> ReActAgent:
    """
    创建技能创建助手 Agent

    这个 Agent 专门用于帮助用户通过对话式交互创建 AgentScope 技能。
    它使用 4 个渐进式问题收集用户需求，并生成技能配置。

    Args:
        model_name: 模型名称，默认 "qwen-max"
        api_key: API Key
        temperature: 温度参数，默认 0.1（降低以提高 JSON 格式准确性）
        project_name: AgentScope 项目名称，用于 Studio 监控

    Returns:
        ReActAgent 实例

    Examples:
        >>> import asyncio
        >>> from agentscope.message import Msg
        >>> agent = create_skill_creator_agent()
        >>> response = await agent(Msg(name="user", content="我想创建一个技能"))
    """
    # 初始化 AgentScope（连接 Studio）
    from .config.agent_config import init_agentscope
    from agentscope.tool import Toolkit
    from agentscope.tool._response import ToolResponse

    init_agentscope(project=project_name)
    logger.info(f"AgentScope initialized for project: {project_name}, Studio: http://localhost:3000")

    # 创建模型实例
    logger.info(f"Creating model with: model_name={model_name}, api_key={api_key}, temperature={temperature}")
    model = create_model(
        model_type=ModelType.QWEN,
        model_name=model_name,
        api_key=api_key,
        temperature=temperature,
    )
    logger.info(f"Model created: {type(model)}")

    # 获取 formatter
    formatter = get_formatter(ModelType.QWEN)
    logger.info(f"Formatter created: {type(formatter)}")

    # 创建一个简单的 toolkit（ReActAgent 需要 toolkit 才能正常工作）
    toolkit = Toolkit()
    logger.info(f"Toolkit created: {type(toolkit)}")

    # 添加确认信息工具
    def confirm_information(info_type: str) -> ToolResponse:
        """确认已收集到足够的信息，可以进入下一阶段

        Args:
            info_type: 信息类型（如 "core_value", "usage_scenario" 等）
        """
        return ToolResponse(content=[{"text": f"已确认收集到足够的 {info_type} 信息，可以进入下一阶段。"}])

    # 添加请求更多信息工具
    def request_more_info(question: str, options: list = None) -> ToolResponse:
        """请求用户提供更多信息

        Args:
            question: 追问的问题
            options: 可选的推荐选项列表
        """
        if options:
            text = f"追问：{question}\n推荐选项：{', '.join(options)}"
        else:
            text = f"追问：{question}"
        return ToolResponse(content=[{"text": text}])

    # 注册工具到 toolkit
    toolkit.register_tool_function(confirm_information)
    toolkit.register_tool_function(request_more_info)

    # 创建 Skill Creator Agent
    logger.info(f"About to create ReActAgent with the following parameters:")
    logger.info(f"  name: skill_creator_assistant")
    logger.info(f"  sys_prompt length: {len(SKILL_CREATOR_SYSTEM_PROMPT)}")
    logger.info(f"  model type: {type(model)}")
    logger.info(f"  formatter type: {type(formatter)}")
    logger.info(f"  toolkit type: {type(toolkit)}")

    # 检查 ReActAgent 的签名
    import inspect
    sig = inspect.signature(ReActAgent.__init__)
    logger.info(f"ReActAgent.__init__ signature: {sig}")

    agent = ReActAgent(
        name="skill_creator_assistant",
        sys_prompt=SKILL_CREATOR_SYSTEM_PROMPT,
        model=model,
        formatter=formatter,
        toolkit=toolkit,
    )

    logger.info(f"Skill Creator Agent '{agent.name}' created successfully with {len(toolkit.get_json_schemas())} tools")
    return agent

