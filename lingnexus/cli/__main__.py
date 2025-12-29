"""
命令行入口
允许通过 python -m lingnexus.cli 运行交互式工具
"""

import asyncio
from .interactive import main

if __name__ == "__main__":
    asyncio.run(main())
