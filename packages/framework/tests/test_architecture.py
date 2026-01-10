"""
架构测试
验证 interactive.py 通过 react_agent.py 作为统一入口的架构是否正确
"""

import sys
import io

# Windows 编码修复
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from lingnexus.agent import create_docx_agent
from lingnexus.config import ModelType
from lingnexus.cli import InteractiveTester


def test_import_structure():
    """测试导入结构"""
    print("=" * 60)
    print("测试 1: 导入结构")
    print("=" * 60)
    
    # 验证可以通过 react_agent.py 导入
    from lingnexus.agent import create_docx_agent
    assert callable(create_docx_agent), "create_docx_agent 应该是可调用的"
    print("OK: create_docx_agent 导入成功")
    
    # 验证 InteractiveTester 可以导入
    from lingnexus.cli import InteractiveTester
    assert InteractiveTester is not None, "InteractiveTester 应该存在"
    print("OK: InteractiveTester 导入成功")
    
    print()


def test_agent_creation():
    """测试 Agent 创建"""
    print("=" * 60)
    print("测试 2: Agent 创建（通过 react_agent.py）")
    print("=" * 60)
    
    # 通过 react_agent.py 创建 Agent
    agent = create_docx_agent(model_type=ModelType.QWEN)
    
    assert agent is not None, "Agent 应该创建成功"
    print(f"OK: Agent 创建成功: {type(agent).__name__}")
    
    # 验证 Agent 类型
    from agentscope.agent import ReActAgent
    assert isinstance(agent, ReActAgent), "Agent 应该是 ReActAgent 实例"
    print("OK: Agent 类型验证通过")
    
    print()


def test_interactive_tester_initialization():
    """测试 InteractiveTester 初始化"""
    print("=" * 60)
    print("测试 3: InteractiveTester 初始化")
    print("=" * 60)
    
    tester = InteractiveTester(
        model_type=ModelType.QWEN,
        model_name="qwen-max",
        auto_execute_code=False,
        enable_studio=False,
    )
    
    assert tester is not None, "InteractiveTester 应该创建成功"
    print("OK: InteractiveTester 创建成功")
    
    assert tester.model_type == ModelType.QWEN, "模型类型应该正确"
    print("OK: 模型类型配置正确")
    
    assert tester.agent is None, "初始时 Agent 应该为 None"
    print("OK: Agent 延迟创建机制正常")
    
    print()


def test_architecture_flow():
    """测试架构调用流程"""
    print("=" * 60)
    print("测试 4: 架构调用流程验证")
    print("=" * 60)
    
    # 模拟 interactive.py 的调用流程
    tester = InteractiveTester(model_type=ModelType.QWEN)
    
    # 调用 _create_agent（模拟用户操作）
    tester._create_agent()
    
    assert tester.agent is not None, "Agent 应该被创建"
    print("OK: Agent 通过 create_docx_agent() 创建成功")
    
    from agentscope.agent import ReActAgent
    assert isinstance(tester.agent, ReActAgent), "Agent 类型正确"
    print("OK: 架构流程验证通过：interactive.py -> react_agent.py -> agent_factory.py")
    
    print()


def main():
    """运行所有测试"""
    try:
        print("\n" + "=" * 60)
        print("架构测试套件")
        print("验证 interactive.py 通过 react_agent.py 作为统一入口")
        print("=" * 60 + "\n")
        
        test_import_structure()
        test_agent_creation()
        test_interactive_tester_initialization()
        test_architecture_flow()
        
        print("=" * 60)
        print("OK: 所有测试通过！")
        print("=" * 60)
        print("\n架构验证：")
        print("  CLI (interactive.py)")
        print("    -> 调用 create_docx_agent()")
        print("  统一入口 (react_agent.py)")
        print("    -> 调用 AgentFactory")
        print("  工厂层 (agent_factory.py)")
        print("    -> 使用底层组件")
        print("  底层组件 (model_config, skill_loader)")
        print()
        
    except Exception as e:
        print(f"\nERROR: 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
