"""
docx Agent 使用示例
演示如何使用 ReActAgent 调用 docx 技能

注意：
- ReActAgent 需要直接传入模型实例，不支持 model_config_name
- agentscope.init() 主要用于全局配置（日志、Studio等），不用于模型配置
- 模型配置通过 model_config.py 中的函数直接创建模型实例
"""

import sys
import io
import os
import asyncio

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from lingnexus.agent import create_docx_agent, AgentFactory
from lingnexus.config import ModelType, init_agentscope
from agentscope.message import Msg


def example_1_basic_usage():
    """示例 1: 基础使用"""
    print("=" * 60)
    print("示例 1: 基础使用 - 创建 docx Agent")
    print("=" * 60)
    
    # 可选：初始化全局配置（日志、Studio等）
    # init_agentscope(project="LingNexus", logging_path="./logs")
    
    # 检查 API Key
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("⚠️  警告: 未设置 DASHSCOPE_API_KEY 环境变量")
        print("   请设置环境变量或直接在代码中提供 api_key")
        return
    
    # 创建 Agent（使用 Qwen 模型）
    agent = create_docx_agent(
        model_type=ModelType.QWEN,
        model_name="qwen-max",
        api_key=api_key,
        temperature=0.5,
    )
    
    print("✅ Agent 创建成功")
    print(f"   模型: Qwen Max")
    print(f"   技能: docx")
    print()
    
    # 使用 Agent
    user_input = "请帮我创建一个新的 Word 文档，标题是'项目计划'"
    print(f"用户输入: {user_input}")
    print()
    
    try:
        # ReActAgent 的 __call__ 是异步方法，需要传入 Msg 对象
        async def call_agent():
            # 创建用户消息，需要指定 role='user'
            user_msg = Msg(name="user", role="user", content=user_input)
            response = await agent(user_msg)
            return response
        
        response = asyncio.run(call_agent())
        print("\nAgent 响应:")
        # 提取响应内容
        if hasattr(response, 'content'):
            if isinstance(response.content, list):
                # 提取文本内容
                text_content = ""
                for item in response.content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_content += item.get('text', '')
                    elif isinstance(item, str):
                        text_content += item
                print(text_content if text_content else response.content)
            else:
                print(response.content)
        else:
            print(response)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


def example_2_deepseek_model():
    """示例 2: 使用 DeepSeek 模型"""
    print("\n" + "=" * 60)
    print("示例 2: 使用 DeepSeek 模型")
    print("=" * 60)
    
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("⚠️  警告: 未设置 DASHSCOPE_API_KEY 环境变量")
        return
    
    # 使用 DeepSeek 模型
    agent = create_docx_agent(
        model_type=ModelType.DEEPSEEK,
        model_name="deepseek-chat",
        api_key=api_key,
        temperature=0.7,
    )
    
    print("✅ Agent 创建成功")
    print(f"   模型: DeepSeek Chat")
    print(f"   技能: docx")
    print()


def example_3_custom_agent():
    """示例 3: 使用工厂类创建自定义 Agent"""
    print("\n" + "=" * 60)
    print("示例 3: 使用工厂类创建自定义 Agent")
    print("=" * 60)
    
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("⚠️  警告: 未设置 DASHSCOPE_API_KEY 环境变量")
        return
    
    factory = AgentFactory()
    
    # 创建自定义 Agent
    agent = factory.create_docx_agent(
        model_type=ModelType.QWEN,
        model_name="qwen-plus",  # 使用 qwen-plus 模型
        api_key=api_key,
        temperature=0.3,  # 更低的温度，输出更确定
        system_prompt="你是一个专业的文档处理专家，专注于创建高质量的 Word 文档。",
    )
    
    print("✅ 自定义 Agent 创建成功")
    print(f"   模型: Qwen Plus")
    print(f"   温度: 0.3")
    print(f"   自定义系统提示词: 已设置")
    print()


def example_4_multi_skill():
    """示例 4: 多技能 Agent（Phase 2 功能预览）"""
    print("\n" + "=" * 60)
    print("示例 4: 多技能 Agent")
    print("=" * 60)
    
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("⚠️  警告: 未设置 DASHSCOPE_API_KEY 环境变量")
        return
    
    factory = AgentFactory()
    
    # 创建支持多个技能的 Agent
    agent = factory.create_multi_skill_agent(
        skills=["docx", "pdf"],  # 支持 docx 和 pdf
        model_type=ModelType.QWEN,
        api_key=api_key,
    )
    
    print("✅ 多技能 Agent 创建成功")
    print(f"   技能: docx, pdf")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("docx Agent 使用示例")
    print("=" * 60)
    print()
    print("注意: 使用前请设置 DASHSCOPE_API_KEY 环境变量")
    print("      export DASHSCOPE_API_KEY=your_api_key")
    print()
    
    # 运行示例
    example_1_basic_usage()
    example_2_deepseek_model()
    example_3_custom_agent()
    example_4_multi_skill()
    
    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)
    print()
    print("💡 提示:")
    print("   - 示例代码展示了如何创建和使用 docx Agent")
    print("   - 可以根据需要修改模型类型、温度等参数")
    print("   - 更多功能请参考文档: docs/design_react_agent_with_skills.md")

