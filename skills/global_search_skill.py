#!/usr/bin/env python3
"""
L0 智能网关：全局情报搜索统一入口
安全策略：最后一层兜底防线，捕获所有越界逃逸错误
"""

import sys
import json
from pathlib import Path
from enum import Enum

# 添加引擎路径
sys.path.append(str(Path(__file__).parent.parent))

from engines.medical_engine import search_medical_db
from engines.browser_engine import fetch_webpage_content


class SearchDomain(str, Enum):
    """搜索域枚举"""
    PUBMED = "pubmed"
    GENERAL_WEB = "general_web"


def global_intelligence_search(query: str, domain: str) -> str:
    """
    全局情报搜索统一入口

    Args:
        query: 搜索关键词（PubMed）或目标 URL（通用网页）
        domain: 搜索域 ('pubmed' | 'general_web')

    Returns:
        搜索结果文本或错误信息
    """
    try:
        # 参数验证
        if not query or not isinstance(query, str):
            return "错误: query 参数无效，必须为非空字符串"

        if not domain or not isinstance(domain, str):
            return "错误: domain 参数无效，必须为非空字符串"

        domain_lower = domain.lower().strip()

        # 路由逻辑
        if domain_lower == SearchDomain.PUBMED:
            # 路由到医疗数据库引擎
            result = search_medical_db(query, source='pubmed', max_results=10)
            return f"=== PubMed 检索结果 ===\n关键词: {query}\n\n{result}"

        elif domain_lower == SearchDomain.GENERAL_WEB:
            # 路由到浏览器引擎
            result = fetch_webpage_content(query, timeout=15)
            return f"=== 网页抓取结果 ===\nURL: {query}\n\n{result}"

        else:
            return f"错误: 不支持的 domain '{domain}'，仅支持 'pubmed' 或 'general_web'"

    except Exception as e:
        # 最后一层兜底防线
        return f"L0 网关兜底捕获异常: {type(e).__name__} - {str(e)}"


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("用法: global_search_skill.py <query> <domain>")
        print("示例: global_search_skill.py 'PROTAC BRD4' pubmed")
        print("示例: global_search_skill.py 'https://example.com' general_web")
        sys.exit(1)

    query = sys.argv[1]
    domain = sys.argv[2]

    result = global_intelligence_search(query, domain)
    print(result)


if __name__ == "__main__":
    main()
