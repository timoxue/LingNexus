"""
交互式测试入口脚本
快速启动交互式测试工具
"""

import sys
import io

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import asyncio
from lingnexus.cli import InteractiveTester
from lingnexus.config import ModelType


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LingNexus 交互式测试工具")
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
        '--mode',
        choices=['chat', 'test'],
        default='test',
        help='初始模式 (默认: test)'
    )
    parser.add_argument(
        '--no-execute',
        action='store_true',
        help='不自动执行代码'
    )
    parser.add_argument(
        '--studio',
        action='store_true',
        help='启用 Studio'
    )
    
    args = parser.parse_args()
    
    model_type = ModelType.QWEN if args.model == 'qwen' else ModelType.DEEPSEEK
    model_name = args.model_name or ("qwen-max" if args.model == 'qwen' else "deepseek-chat")
    
    tester = InteractiveTester(
        model_type=model_type,
        model_name=model_name,
        auto_execute_code=not args.no_execute,
        enable_studio=args.studio,
    )
    tester.current_mode = args.mode
    
    await tester.run()


if __name__ == "__main__":
    asyncio.run(main())

