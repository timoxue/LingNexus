"""
AgentScope Studio 集成示例
演示如何在 LingNexus 中使用 AgentScope Studio

前置要求：
1. 安装 Studio: npm install -g @agentscope/studio
2. 启动 Studio: as_studio
3. 确保 Studio 在 http://localhost:3000 运行
"""

import sys
import io
import os

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from lingnexus.config import init_agentscope, ModelType
from lingnexus.agent import create_docx_agent


def main():
    """主函数"""
    print("=" * 60)
    print("AgentScope Studio 集成示例")
    print("=" * 60)
    print()
    print("前置要求：")
    print("1. 安装 Studio: npm install -g @agentscope/studio")
    print("2. 启动 Studio: as_studio")
    print("3. 确保 Studio 在 http://localhost:3000 运行")
    print()
    
    # 检查是否启用 Studio
    enable_studio = os.getenv("ENABLE_STUDIO", "false").lower() == "true"
    
    if enable_studio:
        print("✅ 启用 AgentScope Studio")
        print("   请在浏览器中访问: http://localhost:3000")
        print()
        
        # 初始化 AgentScope，连接到 Studio
        init_agentscope(
            project="LingNexus",
            name="studio_demo",
            studio_url="http://localhost:3000",
            logging_path="./logs",
            logging_level="INFO",
        )
    else:
        print("ℹ️  Studio 未启用（设置环境变量 ENABLE_STUDIO=true 启用）")
        print("   使用日志模式")
        print()
        
        # 只使用日志，不连接 Studio
        init_agentscope(
            project="LingNexus",
            name="studio_demo",
            logging_path="./logs",
            logging_level="INFO",
        )
    
    # 创建 Agent
    print("创建 docx Agent...")
    agent = create_docx_agent(
        model_type=ModelType.QWEN,
        model_name="qwen-max",
        temperature=0.5,
    )
    print("✅ Agent 创建成功")
    print()
    
    # 使用 Agent（运行情况会在 Studio 中显示）
    print("发送请求到 Agent...")
    user_input = "请简单介绍一下 docx 技能的功能"
    print(f"用户输入: {user_input}")
    print()
    
    try:
        import asyncio
        from agentscope.message import Msg
        
        # ReActAgent 的 __call__ 是异步方法，需要传入 Msg 对象
        async def call_agent():
            user_msg = Msg(name="user", role="user", content=user_input)
            response = await agent(user_msg)
            return response
        
        response = asyncio.run(call_agent())
        
        print("Agent 响应:")
        # 提取响应内容
        if hasattr(response, 'content'):
            if isinstance(response.content, list):
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
        print()
        
        if enable_studio:
            print("=" * 60)
            print("💡 提示:")
            print("   请在 Studio 中查看详细的执行过程：")
            print("   - 消息流")
            print("   - 推理过程")
            print("   - 工具调用")
            print("   http://localhost:3000")
            print("=" * 60)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

