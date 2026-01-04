"""
渐进式披露 Agent 示例
演示如何使用 qwen-max 作为 orchestrator，实现 Claude Skills 的渐进式披露机制
"""

import asyncio
import sys
import io
from pathlib import Path

# Windows 编码修复
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from agentscope.message import Msg
from lingnexus.agent import create_progressive_agent
from lingnexus.config import init_agentscope


async def main():
    """主函数"""
    print("=" * 60)
    print("渐进式披露 Agent 示例")
    print("=" * 60)
    print()
    
    # 初始化 AgentScope
    print("📦 初始化 AgentScope...")
    init_agentscope()
    print("✅ AgentScope 初始化完成")
    print()
    
    # 创建支持渐进式披露的 Agent
    print("🤖 创建渐进式披露 Agent（使用 qwen-max 作为 orchestrator）...")
    agent = create_progressive_agent(
        model_name="qwen-max",
        temperature=0.3,  # orchestrator 使用较低温度
        max_tokens=4096,
    )
    print("✅ Agent 创建完成")
    print()
    
    # 示例 1: 创建 Word 文档
    print("=" * 60)
    print("示例 1: 创建 Word 文档")
    print("=" * 60)
    print()
    
    user_msg_1 = Msg(
        name="user",
        role="user",
        content="请创建一个 Word 文档，内容是关于 Python 编程的简介，包含标题和3个段落"
    )
    
    print(f"👤 用户: {user_msg_1.content}")
    print()
    print("🤖 Agent 处理中...")
    print("   (Agent 会自动按需加载 docx 技能的完整指令)")
    print()
    
    response_1 = await agent(user_msg_1)
    print(f"🤖 Agent: {response_1.content}")
    print()
    
    # 示例 2: 列出可用技能
    print("=" * 60)
    print("示例 2: 列出可用技能")
    print("=" * 60)
    print()
    
    user_msg_2 = Msg(
        name="user",
        role="user",
        content="请列出所有可用的技能"
    )
    
    print(f"👤 用户: {user_msg_2.content}")
    print()
    print("🤖 Agent 处理中...")
    print()
    
    response_2 = await agent(user_msg_2)
    print(f"🤖 Agent: {response_2.content}")
    print()
    
    # 示例 3: 处理 PDF 文档
    print("=" * 60)
    print("示例 3: 处理 PDF 文档")
    print("=" * 60)
    print()
    
    user_msg_3 = Msg(
        name="user",
        role="user",
        content="我想了解 PDF 技能的功能"
    )
    
    print(f"👤 用户: {user_msg_3.content}")
    print()
    print("🤖 Agent 处理中...")
    print("   (Agent 会自动加载 pdf 技能的完整指令)")
    print()
    
    response_3 = await agent(user_msg_3)
    print(f"🤖 Agent: {response_3.content}")
    print()
    
    print("=" * 60)
    print("示例完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())


