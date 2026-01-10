"""
Skill 执行测试脚本（整合版）
验证 docx 技能是否被调用并生成文件

支持多种测试模式：
1. simple - 简单测试（快速验证）
2. basic - 基础测试（不执行代码）
3. full - 完整测试（包含代码提取和执行）
"""

import sys
import io
import os
import asyncio
import argparse
from pathlib import Path
from typing import Optional

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from lingnexus.config import init_agentscope, ModelType
from lingnexus.agent import create_docx_agent
from agentscope.message import Msg
from lingnexus.utils.code_executor import extract_and_execute_code


def extract_response_text(response) -> str:
    """提取 Agent 响应的文本内容"""
    response_text = ""
    if hasattr(response, 'content'):
        if isinstance(response.content, list):
            for item in response.content:
                if isinstance(item, dict) and item.get('type') == 'text':
                    response_text += item.get('text', '')
                elif isinstance(item, str):
                    response_text += item
        else:
            response_text = str(response.content)
    else:
        response_text = str(response)
    return response_text


def verify_file(test_file: Path) -> bool:
    """验证文件是否创建并显示内容"""
    if not test_file.exists():
        return False
    
    file_size = test_file.stat().st_size
    print(f"✅ 文件创建成功！")
    print(f"   文件: {test_file.absolute()}")
    print(f"   大小: {file_size} 字节")
    
    # 读取文件内容
    try:
        from docx import Document
        doc = Document(test_file)
        print(f"\n   文件内容:")
        for i, para in enumerate(doc.paragraphs[:10], 1):
            if para.text.strip():
                print(f"   {i}. {para.text}")
        return True
    except ImportError:
        print("   ⚠️  python-docx 未安装，无法读取文件内容")
        print("   安装命令: pip install python-docx")
        return True
    except Exception as e:
        print(f"   ⚠️  读取文件时出错: {e}")
        return True


async def test_simple_mode(test_file: Path, model_type: ModelType, model_name: str):
    """简单测试模式：快速验证技能调用"""
    print("=" * 60)
    print("测试模式: 简单测试（快速验证）")
    print("=" * 60)
    print()
    
    # 初始化
    enable_studio = os.getenv("ENABLE_STUDIO", "false").lower() == "true"
    if enable_studio:
        init_agentscope(
            project="LingNexus",
            name="skill_test_simple",
            studio_url="http://localhost:3000",
            logging_path="./logs",
        )
        print("✅ 已连接到 Studio")
    else:
        init_agentscope(project="LingNexus", logging_path="./logs")
    
    # 创建 Agent
    print("创建 Agent...")
    agent = create_docx_agent(model_type=model_type, model_name=model_name)
    print("✅ Agent 创建成功\n")
    
    # 删除已存在的测试文件
    if test_file.exists():
        test_file.unlink()
    
    # 请求创建文件
    user_input = f"请创建一个 Word 文档，文件名为 '{test_file.name}'，标题为'测试文档'，内容只有一行：'这是一个测试文档'"
    print(f"用户请求: {user_input}\n")
    
    # 调用 Agent
    print("调用 Agent...")
    user_msg = Msg(name="user", role="user", content=user_input)
    response = await agent(user_msg)
    response_text = extract_response_text(response)
    print("✅ Agent 响应完成\n")
    
    # 检查是否包含代码
    has_code = '```python' in response_text or '```' in response_text
    if has_code:
        print("✅ Agent 提供了代码\n")
        
        # 提取并执行代码
        print("提取并执行代码...")
        result = extract_and_execute_code(response_text)
        
        if result.get('code'):
            print("✅ 代码提取成功")
            if result['success']:
                print("✅ 代码执行成功")
                if result.get('output'):
                    print(f"输出: {result['output']}")
            else:
                print(f"❌ 代码执行失败: {result.get('error', 'Unknown error')}")
        else:
            print("⚠️  未找到可执行代码")
    else:
        print("⚠️  Agent 响应中未包含代码块")
    
    # 验证文件
    print("\n" + "=" * 60)
    print("验证文件创建")
    print("=" * 60)
    
    if not verify_file(test_file):
        print(f"❌ 文件未创建: {test_file}")
        print("\n💡 提示:")
        print("   - Agent 可能只提供了代码，需要手动执行")
        print("   - 检查 Agent 响应中的代码")
        print("   - 在 Studio 中查看详细执行过程")


async def test_basic_mode(test_file: Path, model_type: ModelType, model_name: str):
    """基础测试模式：不执行代码，只验证 Agent 响应"""
    print("=" * 60)
    print("测试模式: 基础测试（不执行代码）")
    print("=" * 60)
    print()
    
    # 初始化
    enable_studio = os.getenv("ENABLE_STUDIO", "false").lower() == "true"
    if enable_studio:
        init_agentscope(
            project="LingNexus",
            name="skill_test_basic",
            studio_url="http://localhost:3000",
            logging_path="./logs",
        )
        print("✅ 已连接到 Studio")
    else:
        init_agentscope(project="LingNexus", logging_path="./logs")
    
    # 创建 Agent
    print("创建 docx Agent...")
    agent = create_docx_agent(model_type=model_type, model_name=model_name)
    print("✅ Agent 创建成功\n")
    
    # 删除已存在的测试文件
    if test_file.exists():
        print(f"⚠️  删除已存在的测试文件: {test_file}")
        test_file.unlink()
    
    # 请求创建文件
    user_input = f"请创建一个新的 Word 文档，文件名为 '{test_file.name}'，标题为'测试文档'，内容包含：\n1. 这是一个测试文档\n2. 用于验证 docx 技能是否正常工作\n3. 创建时间：2025-12-29"
    print(f"用户输入: {user_input}\n")
    
    # 调用 Agent
    print("正在调用 Agent...")
    user_msg = Msg(name="user", role="user", content=user_input)
    response = await agent(user_msg)
    response_text = extract_response_text(response)
    
    # 显示 Agent 响应
    print("\nAgent 响应:")
    print(response_text)
    print()
    
    # 检查是否包含代码
    has_code = '```python' in response_text or '```' in response_text
    if has_code:
        print("✅ Agent 响应中包含代码块")
        print("💡 提示: 可以使用 'full' 模式自动执行代码")
    else:
        print("⚠️  Agent 响应中未包含代码块")
    
    # 验证文件（可能未创建，因为代码未执行）
    print("\n" + "=" * 60)
    print("验证文件创建")
    print("=" * 60)
    
    if verify_file(test_file):
        print("\n✅ 文件已创建（可能是之前测试留下的）")
    else:
        print(f"❌ 文件未创建: {test_file}")
        print("\n💡 提示:")
        print("   - 这是正常的，因为基础模式不执行代码")
        print("   - 使用 'full' 模式可以自动执行代码并创建文件")


async def test_full_mode(test_file: Path, model_type: ModelType, model_name: str):
    """完整测试模式：包含代码提取和执行"""
    print("=" * 60)
    print("测试模式: 完整测试（包含代码执行）")
    print("=" * 60)
    print()
    
    # 初始化
    enable_studio = os.getenv("ENABLE_STUDIO", "false").lower() == "true"
    if enable_studio:
        init_agentscope(
            project="LingNexus",
            name="skill_test_full",
            studio_url="http://localhost:3000",
            logging_path="./logs",
        )
        print("✅ 已连接到 Studio")
        print("   可在 Studio 中查看工具调用详情: http://localhost:3000")
        print()
    else:
        init_agentscope(project="LingNexus", logging_path="./logs")
    
    # 创建 Agent
    print("创建 docx Agent...")
    agent = create_docx_agent(model_type=model_type, model_name=model_name)
    print("✅ Agent 创建成功\n")
    
    # 删除已存在的测试文件
    if test_file.exists():
        print(f"⚠️  删除已存在的测试文件: {test_file}")
        test_file.unlink()
    
    # 请求创建文件
    user_input = f"请创建一个新的 Word 文档，文件名为 '{test_file.name}'，标题为'测试文档'，内容包含：\n1. 这是一个测试文档\n2. 用于验证 docx 技能是否正常工作\n3. 创建时间：2025-12-29\n\n请提供可以直接执行的 Python 代码。"
    print(f"用户输入: {user_input}\n")
    
    # 调用 Agent
    print("正在调用 Agent...")
    user_msg = Msg(name="user", role="user", content=user_input)
    response = await agent(user_msg)
    response_text = extract_response_text(response)
    
    print("\nAgent 响应:")
    print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
    print()
    
    # 提取并执行代码
    print("=" * 60)
    print("提取并执行代码")
    print("=" * 60)
    
    code_result = extract_and_execute_code(response_text, working_dir=Path.cwd())
    
    if code_result.get('code'):
        print("✅ 找到 Python 代码")
        print("\n提取的代码:")
        print("-" * 60)
        print(code_result['code'][:300] + "..." if len(code_result['code']) > 300 else code_result['code'])
        print("-" * 60)
        print()
        
        if code_result['success']:
            print("✅ 代码执行成功")
            if code_result.get('output'):
                print(f"输出: {code_result['output']}")
        else:
            print("❌ 代码执行失败")
            if code_result.get('error'):
                print(f"错误: {code_result['error']}")
    else:
        print("⚠️  未找到可执行的 Python 代码")
        print("Agent 可能只提供了说明，没有提供代码")
    
    # 验证文件
    print("\n" + "=" * 60)
    print("验证文件创建")
    print("=" * 60)
    
    if not verify_file(test_file):
        print(f"❌ 文件未创建: {test_file}")
        print("\n可能的原因:")
        print("   1. Agent 没有提供可执行的代码")
        print("   2. 代码执行失败")
        print("   3. 代码中的文件路径不正确")
        
        if code_result.get('error'):
            print(f"\n执行错误详情:")
            print(code_result['error'])


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Skill 执行测试脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
测试模式说明:
  simple  - 简单测试（快速验证，自动执行代码）
  basic   - 基础测试（不执行代码，只验证 Agent 响应）
  full    - 完整测试（包含代码提取和执行，详细输出）

示例:
  # 简单测试
  python tests/test_skill_execution.py --mode simple

  # 基础测试（不执行代码）
  python tests/test_skill_execution.py --mode basic

  # 完整测试（默认）
  python tests/test_skill_execution.py --mode full

  # 使用 DeepSeek 模型
  python tests/test_skill_execution.py --model deepseek

  # 启用 Studio
  $env:ENABLE_STUDIO="true"
  python tests/test_skill_execution.py
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['simple', 'basic', 'full'],
        default='simple',
        help='测试模式 (默认: simple)'
    )
    
    parser.add_argument(
        '--model',
        choices=['qwen', 'deepseek'],
        default='qwen',
        help='模型类型 (默认: qwen)'
    )
    
    parser.add_argument(
        '--model-name',
        type=str,
        default=None,
        help='模型名称（如 qwen-max, deepseek-chat）'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='输出文件名（默认: test_output.docx）'
    )
    
    args = parser.parse_args()
    
    # 确定模型类型和名称
    model_type = ModelType.QWEN if args.model == 'qwen' else ModelType.DEEPSEEK
    model_name = args.model_name or ("qwen-max" if args.model == 'qwen' else "deepseek-chat")
    
    # 确定输出文件
    output_file = Path(args.output) if args.output else Path("test_output.docx")
    
    print("\n" + "=" * 60)
    print("Skill 执行测试")
    print("=" * 60)
    print(f"测试模式: {args.mode}")
    print(f"模型类型: {args.model} ({model_name})")
    print(f"输出文件: {output_file}")
    print("=" * 60)
    print()
    
    # 根据模式运行测试
    if args.mode == 'simple':
        await test_simple_mode(output_file, model_type, model_name)
    elif args.mode == 'basic':
        await test_basic_mode(output_file, model_type, model_name)
    elif args.mode == 'full':
        await test_full_mode(output_file, model_type, model_name)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    print()
    print("💡 提示:")
    print("   - 使用 --help 查看所有选项")
    print("   - 设置 ENABLE_STUDIO=true 启用 Studio 监控")
    print("   - 更多信息请查看: docs/skill_testing_summary.md")


if __name__ == "__main__":
    asyncio.run(main())
