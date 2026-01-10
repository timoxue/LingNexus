"""
AgentScope Alias 功能示例
展示如何使用 alias 简化模型和 Agent 配置
"""

from agentscope.models import read_model_config
from agentscope.agent import ReActAgent
from agentscope import init

# ==================== 方式 1: 使用配置文件 ====================

# config/models.yaml
"""
models:
  qwen-max:
    model: qwen-max
    api_key: ${DASHSCOPE_API_KEY}
    temperature: 0.3

  deepseek:
    model: deepseek-chat
    api_key: ${DASHSCOPE_API_KEY}
    temperature: 0.3
"""

# 初始化 AgentScope（自动加载配置）
init(model_configs="config/models.yaml")

# 使用别名创建模型
model = read_model_config(config_name="qwen-max")


# ==================== 方式 2: 代码中定义别名 ====================

from agentscope.models import DashScopeChatModel

# 定义模型别名
MODEL_ALIASES = {
    # 快速模型（用于测试）
    "fast": {
        "model": "qwen-turbo",
        "temperature": 0.7,
    },

    # 标准模型（用于一般任务）
    "standard": {
        "model": "qwen-max",
        "temperature": 0.3,
    },

    # 创意模型（用于生成任务）
    "creative": {
        "model": "qwen-max",
        "temperature": 0.9,
    },

    # 精确模型（用于分析任务）
    "precise": {
        "model": "deepseek-chat",
        "temperature": 0.1,
    },
}

# 注册所有别名
for alias, config in MODEL_ALIASES.items():
    DashScopeChatModel(
        model_name=config["model"],
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        generate_kwargs={"temperature": config["temperature"]}
    )


# ==================== 方式 3: Agent 别名 ====================

# 创建 Agent 时使用别名
agents = {
    "orchestrator": ReActAgent(
        name="orchestrator",
        model_config_name="precise",  # 使用模型别名
        system_prompt="你是协调器..."
    ),

    "coder": ReActAgent(
        name="coder",
        model_config_name="fast",  # 使用模型别名
        system_prompt="你是程序员..."
    ),

    "writer": ReActAgent(
        name="writer",
        model_config_name="creative",  # 使用模型别名
        system_prompt="你是作家..."
    ),
}

# 通过别名引用 Agent
def get_agent(alias: str) -> ReActAgent:
    """通过别名获取 Agent"""
    return agents[alias]


# ==================== 使用示例 ====================

# 示例 1: 切换模型（无需修改代码）
def process_task(task_type: str):
    """根据任务类型使用不同的模型"""
    if task_type == "test":
        model = read_model_config("fast")  # 快速模型
    elif task_type == "creative":
        model = read_model_config("creative")  # 创意模型
    elif task_type == "analysis":
        model = read_model_config("precise")  # 精确模型

    agent = ReActAgent(model_config_name=model)
    return agent


# 示例 2: A/B 测试
def ab_test(agent_alias: str):
    """测试不同 Agent 的效果"""
    agent_a = get_agent("orchestrator")
    agent_b = get_agent(agent_alias)

    # 对比两个 Agent 的表现
    ...


# ==================== 优势总结 ====================

"""
Alias 功能的优势：

1. ✅ 简化配置
   - "qwen-max" vs {"model": "qwen-max", "temperature": 0.3, ...}

2. ✅ 统一管理
   - 在一个地方定义所有别名
   - 修改别名定义，所有使用处自动更新

3. ✅ 提高可读性
   - model_config_name="precise" 比 model_config_name="deepseek-chat-0.1-temp" 更清晰

4. ✅ 便于切换
   - 开发环境用 "fast"（便宜）
   - 生产环境用 "standard"（质量好）
   - 只需修改别名定义，不需要改代码

5. ✅ 支持 A/B 测试
   - 同一个功能，多个 Agent 别名
   - 轻松对比不同配置的效果
"""


if __name__ == "__main__":
    print("AgentScope Alias 功能示例")
    print()
    print("建议：")
    print("1. 在 config/models.yaml 中定义模型别名")
    print("2. 使用有意义的别名（如 'fast', 'standard', 'precise'）")
    print("3. 避免使用具体模型名作为别名")
    print("4. 保持别名的一致性")
