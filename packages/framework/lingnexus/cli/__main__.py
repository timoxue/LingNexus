"""
LingNexus 统一命令行入口

支持多种命令模式：
- 交互式对话（默认或使用 chat 命令）
- 监控管理（monitor、status、db、search 等命令）
"""

import asyncio
import sys
import argparse
from pathlib import Path


def main():
    """CLI主入口"""
    parser = argparse.ArgumentParser(
        description="LingNexus 统一命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互式对话（默认）
  python -m lingnexus.cli
  python -m lingnexus.cli chat

  # 监控管理
  python -m lingnexus.cli monitor              # 监控所有项目
  python -m lingnexus.cli monitor --project "司美格鲁肽"
  python -m lingnexus.cli status              # 查看监控状态
  python -m lingnexus.cli db                  # 查看数据库
  python -m lingnexus.cli db --project "司美格鲁肽"
  python -m lingnexus.cli search "关键词"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # ========================================
    # chat 命令 - 交互式Agent对话
    # ========================================
    chat_parser = subparsers.add_parser('chat', help='启动交互式Agent对话')
    chat_parser.add_argument(
        '--model',
        choices=['qwen', 'deepseek'],
        default='qwen',
        help='模型类型 (默认: qwen)'
    )
    chat_parser.add_argument(
        '--model-name',
        type=str,
        default=None,
        help='模型名称（如 qwen-max, deepseek-chat）'
    )
    chat_parser.add_argument(
        '--mode',
        choices=['chat', 'test'],
        default='test',
        help='初始模式 (默认: test)'
    )
    chat_parser.add_argument(
        '--no-execute',
        action='store_true',
        help='不自动执行代码'
    )
    chat_parser.add_argument(
        '--studio',
        action='store_true',
        help='启用 AgentScope Studio'
    )
    chat_parser.add_argument(
        '--no-studio',
        action='store_true',
        help='禁用 Studio'
    )

    # ========================================
    # monitor 命令 - 执行监控任务
    # ========================================
    monitor_parser = subparsers.add_parser('monitor', help='执行监控任务')
    monitor_parser.add_argument('--project', '-p', help='指定项目名称')

    # ========================================
    # status 命令 - 查看监控状态
    # ========================================
    status_parser = subparsers.add_parser('status', help='查看监控状态')

    # ========================================
    # db 命令 - 查看数据库
    # ========================================
    db_parser = subparsers.add_parser('db', help='查看数据库')
    db_parser.add_argument('--project', '-p', help='项目名称')
    db_parser.add_argument('--nct', '-n', help='NCT编号')

    # ========================================
    # search 命令 - 搜索向量数据库
    # ========================================
    search_parser = subparsers.add_parser('search', help='搜索向量数据库')
    search_parser.add_argument('query', help='搜索查询')
    search_parser.add_argument('--project', '-p', help='按项目过滤')
    search_parser.add_argument('--n', type=int, default=5, help='返回结果数')

    # ========================================
    # report 命令 - 生成报告
    # ========================================
    report_parser = subparsers.add_parser('report', help='生成报告')
    report_parser.add_argument('--project', '-p', required=True, help='项目名称')
    report_parser.add_argument('--type', '-t', default='weekly', help='报告类型')

    # 解析参数
    args = parser.parse_args()

    # 如果没有指定命令，默认进入交互模式
    if not args.command:
        args.command = 'chat'
        # 创建一个简单的namespace对象用于chat
        args = argparse.Namespace(
            command='chat',
            model='qwen',
            model_name=None,
            mode='test',
            no_execute=False,
            studio=False,
            no_studio=False
        )

    # ========================================
    # 执行对应的命令
    # ========================================
    if args.command == 'chat':
        # 交互式对话模式
        from .interactive import main as interactive_main
        import os

        # 默认开启 Studio（如果环境变量设置了）
        default_studio = os.getenv("ENABLE_STUDIO", "false").lower() == "true"
        enable_studio = args.studio or (default_studio and not args.no_studio)

        # 设置环境变量供interactive模块使用
        if enable_studio:
            os.environ["ENABLE_STUDIO"] = "true"

        # 重新解析参数传给interactive
        import sys
        sys.argv = ['lingnexus.cli']
        if args.model != 'qwen':
            sys.argv.extend(['--model', args.model])
        if args.model_name:
            sys.argv.extend(['--model-name', args.model_name])
        if args.mode != 'test':
            sys.argv.extend(['--mode', args.mode])
        if args.no_execute:
            sys.argv.append('--no-execute')
        if args.studio:
            sys.argv.append('--studio')
        if args.no_studio:
            sys.argv.append('--no-studio')

        asyncio.run(interactive_main())

    elif args.command == 'monitor':
        # 监控命令
        from .monitoring import cmd_monitor
        cmd_monitor(args)

    elif args.command == 'status':
        # 状态命令
        from .monitoring import cmd_status
        cmd_status(args)

    elif args.command == 'db':
        # 数据库查看命令
        from .monitoring import cmd_db
        cmd_db(args)

    elif args.command == 'search':
        # 搜索命令
        from .monitoring import cmd_search
        cmd_search(args)

    elif args.command == 'report':
        # 报告命令
        from .monitoring import cmd_report
        cmd_report(args)


if __name__ == "__main__":
    main()
