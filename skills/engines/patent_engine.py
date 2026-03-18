#!/usr/bin/env python3
"""
L1 引擎层：专利数据库引擎
支持多个专利数据源的统一访问接口

核心策略：
1. 优先使用 PubMed 文献中的专利信息（最可靠）
2. 使用 Google Patents 作为补充验证
3. 对于动态网站，提供智能回退到 PubMed
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Optional

# 导入浏览器引擎和医疗引擎
sys.path.append(str(Path(__file__).parent.parent))
from engines.browser_engine import fetch_webpage_content
from engines.medical_engine import search_medical_db_json


class PatentDatabase:
    """专利数据库枚举"""
    YAOZH = "yaozh"              # 药智网（中国）
    CNIPA = "cnipa"              # 中国国家知识产权局
    JPLATPAT = "jplatpat"        # 日本专利库
    GOOGLE_PATENTS = "google"    # Google Patents
    ESPACENET = "espacenet"      # 欧洲专利局


# 专利数据库 URL 模板
PATENT_DB_URLS = {
    PatentDatabase.YAOZH: "https://db.yaozh.com/patent?q={query}",
    PatentDatabase.CNIPA: "http://epub.cnipa.gov.cn/",
    PatentDatabase.JPLATPAT: "https://www.j-platpat.inpit.go.jp/",
    PatentDatabase.GOOGLE_PATENTS: "https://patents.google.com/?q={query}",
    PatentDatabase.ESPACENET: "https://worldwide.espacenet.com/patent/search?q={query}",
}


def extract_patents_from_pubmed(query: str, max_results: int = 10) -> Dict[str, any]:
    """
    从 PubMed 文献中提取专利信息

    策略：
    1. 搜索相关文献
    2. 从摘要、全文、利益冲突声明中提取专利号
    3. 返回结构化的专利信息

    注意：PubMed API 只返回摘要，专利号通常在全文的利益冲突声明中。
    本函数会返回相关文献列表，建议手动访问全文获取专利信息。

    Args:
        query: 搜索关键词（药物名称、靶点等）
        max_results: 最大文献数

    Returns:
        包含专利信息的字典
    """
    try:
        # 搜索 PubMed 文献
        articles = search_medical_db_json(query, max_results=max_results)

        if not articles:
            return {
                "status": "no_results",
                "message": f"未找到与 '{query}' 相关的文献",
                "patents": [],
                "articles": []
            }

        # 专利号正则表达式
        patent_patterns = [
            r'\b(US\d{7,10}[A-Z]\d?)\b',  # US20240182490A1
            r'\b(CN\d{9}[A-Z])\b',         # CN114269365A
            r'\b(JP\d{7,10}[A-Z]?)\b',     # JP2023123456A
            r'\b(EP\d{7}[A-Z]\d?)\b',      # EP1234567A1
            r'\b(WO\d{4}/\d{6})\b',        # WO2024/123456
        ]

        patents_found = []
        articles_info = []

        for article in articles:
            pmid = article.get('pmid', 'N/A')
            title = article.get('title', '')
            abstract = article.get('abstract', '')
            url = article.get('url', f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/')

            # 保存文章信息（即使没找到专利号也保存，因为全文可能包含）
            articles_info.append({
                "pmid": pmid,
                "title": title,
                "url": url,
                "has_patent_in_abstract": False
            })

            # 合并文本用于搜索
            full_text = f"{title} {abstract}"

            # 提取专利号
            for pattern in patent_patterns:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                for patent_num in matches:
                    patents_found.append({
                        "patent_number": patent_num.upper(),
                        "source_pmid": pmid,
                        "source_title": title[:100],
                        "source_url": url,
                        "context": _extract_context(full_text, patent_num)
                    })
                    articles_info[-1]["has_patent_in_abstract"] = True

        # 去重
        unique_patents = {}
        for p in patents_found:
            pnum = p['patent_number']
            if pnum not in unique_patents:
                unique_patents[pnum] = p

        return {
            "status": "success",
            "query": query,
            "articles_searched": len(articles),
            "patents_found": len(unique_patents),
            "patents": list(unique_patents.values()),
            "articles": articles_info  # 返回所有文章，即使摘要中没有专利号
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"{type(e).__name__}: {str(e)}",
            "patents": [],
            "articles": []
        }


def _extract_context(text: str, patent_num: str, context_chars: int = 150) -> str:
    """提取专利号周围的上下文"""
    try:
        idx = text.upper().find(patent_num.upper())
        if idx == -1:
            return ""

        start = max(0, idx - context_chars)
        end = min(len(text), idx + len(patent_num) + context_chars)

        context = text[start:end]
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."

        return context.strip()
    except:
        return ""


def search_patent_db(
    query: str,
    database: str = PatentDatabase.GOOGLE_PATENTS,
    max_results: int = 10,
    fallback_to_pubmed: bool = True
) -> str:
    """
    搜索专利数据库（智能回退策略）

    Args:
        query: 搜索关键词（药物名称、靶点、专利号等）
        database: 数据库名称（yaozh, cnipa, jplatpat, google, espacenet）
        max_results: 最大结果数
        fallback_to_pubmed: 当专利库访问失败时，是否回退到 PubMed

    Returns:
        专利搜索结果文本
    """
    try:
        # 验证数据库
        if database not in PATENT_DB_URLS:
            return f"错误: 不支持的专利数据库 '{database}'"

        # 对于动态网站，直接使用 PubMed 回退策略
        if database in [PatentDatabase.CNIPA, PatentDatabase.JPLATPAT, PatentDatabase.YAOZH]:
            if fallback_to_pubmed:
                print(f"⚠️ {database.upper()} 需要动态渲染，自动回退到 PubMed 策略")
                return _fallback_to_pubmed_search(query, database)
            else:
                search_url = PATENT_DB_URLS[database].format(query=query)
                return f"""⚠️ {database.upper()} 需要动态渲染支持

数据库: {database}
查询: {query}
URL: {search_url}

建议：使用 fallback_to_pubmed=True 自动切换到 PubMed 策略
"""

        # Google Patents 和 Espacenet - 尝试直接访问
        search_url = PATENT_DB_URLS[database].format(query=query)
        result = fetch_webpage_content(search_url, timeout=30)

        # 检查结果
        if result.startswith("网页") or "NO_RESULTS" in result:
            if fallback_to_pubmed:
                print(f"⚠️ {database.upper()} 直接访问失败，回退到 PubMed 策略")
                return _fallback_to_pubmed_search(query, database)
            else:
                return f"""专利数据库访问受限: {database}

{result}

建议：使用 fallback_to_pubmed=True 自动切换到 PubMed 策略
"""

        return f"=== {database.upper()} 专利搜索结果 ===\n查询: {query}\n\n{result[:2000]}"

    except Exception as e:
        if fallback_to_pubmed:
            print(f"⚠️ 专利搜索异常，回退到 PubMed 策略: {e}")
            return _fallback_to_pubmed_search(query, database)
        return f"专利搜索异常: {database} - {type(e).__name__}: {str(e)}"


def _fallback_to_pubmed_search(query: str, original_database: str) -> str:
    """
    回退到 PubMed 搜索策略

    当专利库无法直接访问时，从 PubMed 文献中提取专利信息
    """
    print(f"🔄 执行 PubMed 回退策略: {query}")

    # 从 PubMed 提取专利
    result = extract_patents_from_pubmed(query, max_results=20)

    if result['status'] == 'error':
        return f"""专利搜索失败（PubMed 回退策略）

原始数据库: {original_database}
查询: {query}
错误: {result.get('error', 'Unknown error')}

建议：
1. 检查查询关键词是否正确
2. 尝试使用更具体的药物名称或靶点
3. 如有具体专利号，使用 search_patent_by_number() 直接查询
"""

    # 格式化输出
    output = [
        f"=== 专利信息（PubMed 回退策略）===",
        f"原始数据库: {original_database}",
        f"查询: {query}",
        f"搜索文献数: {result.get('articles_searched', 0)}",
        f"摘要中找到专利数: {result.get('patents_found', 0)}",
        ""
    ]

    if result.get('patents_found', 0) > 0:
        output.append("✅ 在摘要中找到的专利：")
        for i, patent in enumerate(result['patents'][:10], 1):
            output.append(f"\n{i}. {patent['patent_number']}")
            output.append(f"   来源: PMID {patent['source_pmid']}")
            output.append(f"   文献: {patent['source_title']}")
            output.append(f"   链接: {patent['source_url']}")
            if patent.get('context'):
                output.append(f"   上下文: {patent['context'][:200]}")
    else:
        output.append("⚠️ 摘要中未找到专利号，但找到相关文献。")
        output.append("💡 专利号通常在全文的利益冲突声明（Conflicts of Interest）或致谢（Acknowledgments）部分。")
        output.append("\n相关文献列表（建议访问全文查找专利信息）：")

        for i, article in enumerate(result.get('articles', [])[:10], 1):
            output.append(f"\n{i}. PMID {article['pmid']}")
            output.append(f"   标题: {article['title'][:100]}")
            output.append(f"   链接: {article['url']}")
            output.append(f"   💡 访问全文查看 Conflicts of Interest 部分")

    output.append("\n" + "="*60)
    output.append("📌 使用建议：")
    output.append("1. 访问上述文献的全文（点击 PubMed 链接）")
    output.append("2. 查找文章末尾的 'Conflicts of Interest' 或 'Acknowledgments' 部分")
    output.append("3. 提取专利号后，使用 search_patent_by_number() 获取详情")

    return "\n".join(output)


def search_patent_by_number(patent_number: str) -> Dict[str, str]:
    """
    根据专利号查询专利详情

    Args:
        patent_number: 专利号（如 US20240182490A1, CN114269365A）

    Returns:
        专利详情字典
    """
    try:
        # 根据专利号前缀判断数据库
        if patent_number.startswith("US"):
            url = f"https://patents.google.com/patent/{patent_number}"
        elif patent_number.startswith("CN"):
            url = f"https://patents.google.com/patent/{patent_number}"
        elif patent_number.startswith("JP"):
            url = f"https://patents.google.com/patent/{patent_number}"
        elif patent_number.startswith("EP"):
            url = f"https://worldwide.espacenet.com/patent/search?q={patent_number}"
        else:
            return {"error": f"无法识别的专利号格式: {patent_number}"}

        # 抓取专利页面
        content = fetch_webpage_content(url, timeout=30)

        return {
            "patent_number": patent_number,
            "url": url,
            "content": content[:3000],  # 限制长度
            "status": "success" if not content.startswith("网页") else "failed"
        }

    except Exception as e:
        return {
            "patent_number": patent_number,
            "error": f"{type(e).__name__}: {str(e)}",
            "status": "error"
        }


if __name__ == "__main__":
    # 测试用例
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 patent_engine.py <查询词> [数据库]")
        print("数据库选项: yaozh, cnipa, jplatpat, google, espacenet")
        sys.exit(1)

    query = sys.argv[1]
    database = sys.argv[2] if len(sys.argv) > 2 else PatentDatabase.GOOGLE_PATENTS

    print(f"正在搜索专利数据库: {database}")
    result = search_patent_db(query, database)
    print(result)
