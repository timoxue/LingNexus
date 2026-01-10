"""
Agent 创建测试
测试 docx Agent 的创建
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


def test_create_docx_agent():
    """测试创建 docx Agent"""
    from lingnexus.agent import create_docx_agent
    from lingnexus.config import ModelType
    
    agent = create_docx_agent(
        model_type=ModelType.QWEN,
        model_name="qwen-max",
    )
    
    assert agent is not None, "Agent 创建失败"
    assert agent.name == "docx_assistant", "Agent 名称不正确"
    assert agent.model is not None, "Agent 模型未设置"
    assert agent.formatter is not None, "Agent formatter 未设置"
    
    print(f"✅ Agent 创建成功")
    print(f"   Agent 名称: {agent.name}")
    print(f"   模型: {agent.model.model_name}")
    print(f"   Formatter: {type(agent.formatter).__name__}")
    
    return agent


def test_create_agent_with_factory():
    """测试使用工厂类创建 Agent"""
    from lingnexus.agent import AgentFactory
    from lingnexus.config import ModelType
    
    factory = AgentFactory()
    agent = factory.create_docx_agent(
        model_type=ModelType.QWEN,
        model_name="qwen-max",
    )
    
    assert agent is not None
    print(f"✅ 使用工厂类创建 Agent 成功")
    return agent


if __name__ == "__main__":
    print("=" * 60)
    print("Agent 创建测试")
    print("=" * 60)
    
    try:
        test_create_docx_agent()
        test_create_agent_with_factory()
        print("\n✅ 所有 Agent 创建测试通过")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

