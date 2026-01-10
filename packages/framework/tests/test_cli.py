"""
CLI 测试套件
测试交互式 CLI 工具的各种功能
"""

import sys
import io
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Windows 编码修复
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if hasattr(sys.stderr, 'buffer') and not isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from lingnexus.cli import InteractiveTester
from lingnexus.config import ModelType
from agentscope.message import Msg


class TestInteractiveTester:
    """InteractiveTester 测试类"""
    
    def test_initialization(self):
        """测试初始化"""
        print("\n" + "=" * 60)
        print("测试 1: InteractiveTester 初始化")
        print("=" * 60)
        
        tester = InteractiveTester(
            model_type=ModelType.QWEN,
            model_name="qwen-max",
            auto_execute_code=True,
            enable_studio=False,
        )
        
        assert tester.model_type == ModelType.QWEN, "模型类型应该正确"
        assert tester.model_name == "qwen-max", "模型名称应该正确"
        assert tester.auto_execute_code == True, "自动执行代码应该开启"
        assert tester.enable_studio == False, "Studio 应该关闭"
        assert tester.agent is None, "初始时 Agent 应该为 None"
        assert tester.conversation_history == [], "对话历史应该为空"
        assert tester.current_mode == "chat", "默认模式应该是 chat"
        
        print("OK: 初始化测试通过")
        print()
    
    def test_default_model_name(self):
        """测试默认模型名称"""
        print("=" * 60)
        print("测试 2: 默认模型名称")
        print("=" * 60)
        
        # Qwen 默认名称
        tester_qwen = InteractiveTester(model_type=ModelType.QWEN)
        assert tester_qwen.model_name == "qwen-max", "Qwen 默认名称应该是 qwen-max"
        print("OK: Qwen 默认名称正确")
        
        # DeepSeek 默认名称
        tester_deepseek = InteractiveTester(model_type=ModelType.DEEPSEEK)
        assert tester_deepseek.model_name == "deepseek-chat", "DeepSeek 默认名称应该是 deepseek-chat"
        print("OK: DeepSeek 默认名称正确")
        
        print()
    
    def test_agent_creation(self):
        """测试 Agent 创建"""
        print("=" * 60)
        print("测试 3: Agent 创建")
        print("=" * 60)
        
        tester = InteractiveTester(model_type=ModelType.QWEN)
        
        # 初始时 Agent 应该为 None
        assert tester.agent is None, "初始时 Agent 应该为 None"
        
        # 调用 _create_agent
        agent = tester._create_agent()
        
        assert agent is not None, "Agent 应该被创建"
        assert tester.agent is not None, "Agent 应该被保存"
        
        # 再次调用应该返回同一个实例
        agent2 = tester._create_agent()
        assert agent is agent2, "应该返回同一个 Agent 实例"
        
        print("OK: Agent 创建测试通过")
        print()
    
    def test_command_parsing(self):
        """测试命令解析（通过 _handle_command 内部逻辑）"""
        print("=" * 60)
        print("测试 4: 命令解析")
        print("=" * 60)
        
        tester = InteractiveTester()
        
        # 测试 /help 命令（应该不报错）
        try:
            tester._handle_command("/help")
            print("OK: /help 命令处理正确")
        except Exception as e:
            print(f"ERROR: /help 命令处理失败: {e}")
            raise
        
        # 测试带参数的命令（通过实际调用验证）
        original_mode = tester.current_mode
        tester._handle_command("/mode test")
        assert tester.current_mode == "test", "带参数的命令应该正确执行"
        tester.current_mode = original_mode  # 恢复
        print("OK: 带参数的命令解析正确")
        
        # 测试普通输入（非命令）- 通过检查是否以 / 开头
        is_command = "/help".startswith("/")
        assert is_command == True, "命令应该以 / 开头"
        print("OK: 命令识别正确")
        
        print()
    
    def test_help_command(self):
        """测试 /help 命令"""
        print("=" * 60)
        print("测试 5: /help 命令")
        print("=" * 60)
        
        tester = InteractiveTester()
        
        # 测试 help 命令处理（不实际打印，只验证不报错）
        try:
            tester._handle_command("/help")
            print("OK: /help 命令处理成功")
        except Exception as e:
            print(f"ERROR: /help 命令处理失败: {e}")
            raise
        
        print()
    
    def test_mode_command(self):
        """测试 /mode 命令"""
        print("=" * 60)
        print("测试 6: /mode 命令")
        print("=" * 60)
        
        tester = InteractiveTester()
        
        # 测试切换到 test 模式
        tester._handle_command("/mode test")
        assert tester.current_mode == "test", "应该切换到 test 模式"
        print("OK: 切换到 test 模式成功")
        
        # 测试切换到 chat 模式
        tester._handle_command("/mode chat")
        assert tester.current_mode == "chat", "应该切换到 chat 模式"
        print("OK: 切换到 chat 模式成功")
        
        # 测试无效模式
        original_mode = tester.current_mode
        tester._handle_command("/mode invalid")
        assert tester.current_mode == original_mode, "无效模式不应该改变当前模式"
        print("OK: 无效模式处理正确")
        
        # 测试查询当前模式
        tester._handle_command("/mode")
        print("OK: 查询模式成功")
        
        print()
    
    def test_execute_command(self):
        """测试 /execute 命令"""
        print("=" * 60)
        print("测试 7: /execute 命令")
        print("=" * 60)
        
        tester = InteractiveTester(auto_execute_code=False)
        
        # 测试开启自动执行
        tester._handle_command("/execute on")
        assert tester.auto_execute_code == True, "应该开启自动执行"
        print("OK: 开启自动执行成功")
        
        # 测试关闭自动执行
        tester._handle_command("/execute off")
        assert tester.auto_execute_code == False, "应该关闭自动执行"
        print("OK: 关闭自动执行成功")
        
        # 测试查询状态
        tester._handle_command("/execute")
        print("OK: 查询执行状态成功")
        
        print()
    
    def test_history_command(self):
        """测试 /history 命令"""
        print("=" * 60)
        print("测试 8: /history 命令")
        print("=" * 60)
        
        tester = InteractiveTester()
        
        # 添加一些历史记录
        tester.conversation_history = [
            ("问题1", "回答1"),
            ("问题2", "回答2"),
        ]
        
        # 测试显示历史（不实际打印，只验证不报错）
        try:
            tester._handle_command("/history")
            print("OK: /history 命令处理成功")
        except Exception as e:
            print(f"ERROR: /history 命令处理失败: {e}")
            raise
        
        print()
    
    def test_clear_command(self):
        """测试 /clear 命令"""
        print("=" * 60)
        print("测试 9: /clear 命令")
        print("=" * 60)
        
        tester = InteractiveTester()
        
        # 添加一些历史记录
        tester.conversation_history = [
            ("问题1", "回答1"),
            ("问题2", "回答2"),
        ]
        
        # 测试清空历史
        tester._handle_command("/clear")
        assert len(tester.conversation_history) == 0, "历史应该被清空"
        print("OK: /clear 命令处理成功")
        
        print()
    
    def test_exit_command(self):
        """测试 /exit 命令"""
        print("=" * 60)
        print("测试 10: /exit 命令")
        print("=" * 60)
        
        tester = InteractiveTester()
        
        # 测试退出命令
        result = tester._handle_command("/exit")
        assert result == False, "退出命令应该返回 False"
        print("OK: /exit 命令处理成功")
        
        # 测试 /quit 命令
        tester2 = InteractiveTester()
        result = tester2._handle_command("/quit")
        assert result == False, "/quit 命令应该返回 False"
        print("OK: /quit 命令处理成功")
        
        print()
    
    def test_response_extraction(self):
        """测试响应提取"""
        print("=" * 60)
        print("测试 11: 响应提取")
        print("=" * 60)
        
        tester = InteractiveTester()
        
        # 测试简单字符串响应
        mock_response = Mock()
        mock_response.content = "简单文本响应"
        result = tester._extract_response_text(mock_response)
        assert result == "简单文本响应", "应该提取简单文本"
        print("OK: 简单文本提取成功")
        
        # 测试列表响应
        mock_response2 = Mock()
        mock_response2.content = [
            {"type": "text", "text": "第一部分"},
            {"type": "text", "text": "第二部分"},
        ]
        result = tester._extract_response_text(mock_response2)
        assert result == "第一部分第二部分", "应该提取列表中的文本"
        print("OK: 列表响应提取成功")
        
        # 测试字符串列表响应
        mock_response3 = Mock()
        mock_response3.content = ["文本1", "文本2"]
        result = tester._extract_response_text(mock_response3)
        assert result == "文本1文本2", "应该提取字符串列表"
        print("OK: 字符串列表提取成功")
        
        print()
    
    @patch('lingnexus.cli.interactive.create_docx_agent')
    async def test_agent_call(self, mock_create_agent):
        """测试 Agent 调用"""
        print("=" * 60)
        print("测试 12: Agent 调用")
        print("=" * 60)
        
        # 创建模拟 Agent
        mock_agent = AsyncMock()
        mock_response = Mock()
        mock_response.content = "测试响应"
        mock_agent.return_value = mock_response
        mock_create_agent.return_value = mock_agent
        
        tester = InteractiveTester()
        
        # 调用 Agent
        response = await tester._call_agent("测试问题")
        
        assert response == "测试响应", "应该返回正确的响应"
        assert mock_agent.called, "Agent 应该被调用"
        print("OK: Agent 调用测试通过")
        
        print()
    
    def test_file_listing(self):
        """测试文件列表功能"""
        print("=" * 60)
        print("测试 13: 文件列表功能")
        print("=" * 60)
        
        tester = InteractiveTester()
        
        # 测试列出文件（不实际检查文件系统，只验证不报错）
        try:
            tester._handle_command("/files")
            print("OK: /files 命令处理成功")
        except Exception as e:
            print(f"ERROR: /files 命令处理失败: {e}")
            raise
        
        print()
    
    def test_model_command(self):
        """测试 /model 命令"""
        print("=" * 60)
        print("测试 14: /model 命令")
        print("=" * 60)
        
        tester = InteractiveTester(model_type=ModelType.QWEN)
        
        # 测试切换到 deepseek
        tester._handle_command("/model deepseek")
        assert tester.model_type == ModelType.DEEPSEEK, "应该切换到 deepseek"
        assert tester.model_name == "deepseek-chat", "模型名称应该更新"
        assert tester.agent is None, "Agent 应该被重置"
        print("OK: 切换到 deepseek 成功")
        
        # 测试切换回 qwen
        tester._handle_command("/model qwen")
        assert tester.model_type == ModelType.QWEN, "应该切换到 qwen"
        assert tester.model_name == "qwen-max", "模型名称应该更新"
        print("OK: 切换到 qwen 成功")
        
        # 测试查询当前模型
        tester._handle_command("/model")
        print("OK: 查询模型成功")
        
        print()
    
    def test_status_command(self):
        """测试 /status 命令"""
        print("=" * 60)
        print("测试 15: /status 命令")
        print("=" * 60)
        
        tester = InteractiveTester()
        
        # 测试状态命令（不实际打印，只验证不报错）
        try:
            tester._handle_command("/status")
            print("OK: /status 命令处理成功")
        except Exception as e:
            print(f"ERROR: /status 命令处理失败: {e}")
            raise
        
        print()
    
    def test_unknown_command(self):
        """测试未知命令处理"""
        print("=" * 60)
        print("测试 16: 未知命令处理")
        print("=" * 60)
        
        tester = InteractiveTester()
        
        # 测试未知命令（应该返回 True 继续运行，但显示错误信息）
        result = tester._handle_command("/unknown")
        assert result == True, "未知命令应该返回 True 继续运行"
        print("OK: 未知命令处理正确")
        
        print()


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("CLI 测试套件")
    print("=" * 60 + "\n")
    
    test_instance = TestInteractiveTester()
    
    # 同步测试
    sync_tests = [
        test_instance.test_initialization,
        test_instance.test_default_model_name,
        test_instance.test_agent_creation,
        test_instance.test_command_parsing,
        test_instance.test_help_command,
        test_instance.test_mode_command,
        test_instance.test_execute_command,
        test_instance.test_history_command,
        test_instance.test_clear_command,
        test_instance.test_exit_command,
        test_instance.test_response_extraction,
        test_instance.test_file_listing,
        test_instance.test_model_command,
        test_instance.test_status_command,
        test_instance.test_unknown_command,
    ]
    
    # 异步测试
    async_tests = [
        test_instance.test_agent_call,
    ]
    
    # 运行同步测试
    for test in sync_tests:
        try:
            test()
        except Exception as e:
            print(f"ERROR: {test.__name__} 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # 运行异步测试
    for test in async_tests:
        try:
            asyncio.run(test())
        except Exception as e:
            print(f"ERROR: {test.__name__} 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("=" * 60)
    print("OK: 所有 CLI 测试通过！")
    print("=" * 60)
    print()
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

