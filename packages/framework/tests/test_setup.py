"""
快速测试脚本
验证 API Key、模型创建、Skill 注册和 Agent 创建
"""

import sys
import io
from pathlib import Path

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_api_key():
    """测试 1: API Key 加载"""
    print("=" * 60)
    print("测试 1: API Key 加载")
    print("=" * 60)
    from lingnexus.config import get_dashscope_api_key
    
    key = get_dashscope_api_key()
    if key:
        print(f"✅ API Key 已加载: {key[:10]}...{key[-4:]}")
        print(f"   Key 长度: {len(key)} 字符")
        return True
    else:
        print("❌ API Key 未加载")
        print("   请检查 .env 文件是否存在且包含 DASHSCOPE_API_KEY")
        return False

def test_model_creation():
    """测试 2: 模型创建"""
    print("\n" + "=" * 60)
    print("测试 2: 模型创建")
    print("=" * 60)
    from lingnexus.config import create_model, ModelType
    
    success_count = 0
    
    # 测试 Qwen
    try:
        model = create_model(ModelType.QWEN, model_name="qwen-max")
        print(f"✅ Qwen 模型创建成功: {model.model_name}")
        success_count += 1
    except Exception as e:
        print(f"❌ Qwen 模型创建失败: {e}")
    
    # 测试 DeepSeek
    try:
        model = create_model(ModelType.DEEPSEEK, model_name="deepseek-chat")
        print(f"✅ DeepSeek 模型创建成功: {model.model_name}")
        success_count += 1
    except Exception as e:
        print(f"❌ DeepSeek 模型创建失败: {e}")
    
    return success_count == 2

def test_skill_registration():
    """测试 3: Skill 注册"""
    print("\n" + "=" * 60)
    print("测试 3: Skill 注册")
    print("=" * 60)
    from lingnexus.utils import SkillLoader
    
    try:
        loader = SkillLoader()
        success = loader.register_skill("docx", skill_type="external")
        if success:
            prompt = loader.get_skill_prompt()
            print(f"✅ docx 技能注册成功")
            if prompt:
                print(f"   提示词长度: {len(prompt)} 字符")
                print(f"   预览: {prompt[:100]}...")
            return True
        else:
            print("❌ 技能注册失败")
            return False
    except Exception as e:
        print(f"❌ 注册失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_creation():
    """测试 4: Agent 创建"""
    print("\n" + "=" * 60)
    print("测试 4: Agent 创建")
    print("=" * 60)
    from lingnexus.agent import create_docx_agent
    from lingnexus.config import ModelType
    
    try:
        agent = create_docx_agent(
            model_type=ModelType.QWEN,
            model_name="qwen-max",
        )
        print(f"✅ Agent 创建成功")
        print(f"   Agent 名称: {agent.name}")
        print(f"   模型: {agent.model.model_name}")
        print(f"   Formatter: {type(agent.formatter).__name__}")
        return True
    except Exception as e:
        print(f"❌ Agent 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_call(interactive=True):
    """测试 5: Agent 调用（可选，会消耗 API）"""
    print("\n" + "=" * 60)
    print("测试 5: Agent 调用（可选）")
    print("=" * 60)
    print("⚠️  此测试会实际调用 API，消耗额度")
    print("   如果不想测试，可以跳过")
    
    if not interactive:
        print("   非交互模式，跳过 Agent 调用测试")
        return None
    
    try:
        response = input("\n是否执行此测试？(y/n): ").strip().lower()
        if response != 'y':
            print("   跳过 Agent 调用测试")
            return None
    except (EOFError, KeyboardInterrupt):
        print("   非交互式环境，跳过 Agent 调用测试")
        return None
    
    from lingnexus.agent import create_docx_agent
    from lingnexus.config import ModelType
    
    try:
        agent = create_docx_agent(
            model_type=ModelType.QWEN,
            model_name="qwen-max",
        )
        
        import asyncio
        from agentscope.message import Msg
        
        print("\n   发送测试请求...")
        
        # ReActAgent 的 __call__ 是异步方法，需要传入 Msg 对象
        async def call_agent():
            user_msg = Msg(name="user", role="user", content="请简单介绍一下 docx 技能的功能，用一句话回答即可")
            response = await agent(user_msg)
            return response
        
        response = asyncio.run(call_agent())
        
        print("\n✅ Agent 响应:")
        # 提取响应内容
        if hasattr(response, 'content'):
            if isinstance(response.content, list):
                text_content = ""
                for item in response.content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_content += item.get('text', '')
                    elif isinstance(item, str):
                        text_content += item
                print(f"   {text_content if text_content else response.content}")
            else:
                print(f"   {response.content}")
        else:
            print(f"   {response}")
        return True
    except Exception as e:
        print(f"❌ Agent 调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LingNexus 环境测试")
    print("=" * 60)
    print()
    
    results = []
    
    # 运行基础测试
    results.append(("API Key 加载", test_api_key()))
    results.append(("模型创建", test_model_creation()))
    results.append(("Skill 注册", test_skill_registration()))
    results.append(("Agent 创建", test_agent_creation()))
    
    # 可选：Agent 调用测试（仅在交互式环境中）
    import sys
    is_interactive = sys.stdin.isatty()
    call_result = test_agent_call(interactive=is_interactive)
    if call_result is not None:
        results.append(("Agent 调用", call_result))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, result in results:
        if result is None:
            status = "⏭️  跳过"
        elif result:
            status = "✅ 通过"
        else:
            status = "❌ 失败"
        print(f"{name}: {status}")
    
    # 只统计非跳过的测试
    tested_results = [r for _, r in results if r is not None]
    all_passed = all(tested_results) if tested_results else False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！环境配置正确。")
    else:
        print("❌ 部分测试失败，请检查配置。")
    print("=" * 60)
    print()
    print("💡 提示:")
    print("   - 如果所有基础测试通过，可以开始使用 Agent")
    print("   - 更多示例请查看: examples/docx_agent_example.py")
    print("   - 详细文档请查看: docs/")

