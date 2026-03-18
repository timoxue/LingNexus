"""
L1 引擎层：医疗数据库检索引擎
封装 OpenClaw-Medical-Skills 库的 PubMed API
安全策略：异常捕获 + 熔断保护，返回错误字符串

新增功能：Deep COI Parsing（深度利益冲突解析）
- 从 PubMed 全文中提取 Conflicts of Interest 声明
- 使用正则匹配专利号（WO/US/CN/JP/EP 格式）
- 提取企业授权信息和 Startup 项目线索

优化：指数退避重试机制
- PubMed API 调用超时时自动重试
- 最大重试次数：3 次
- 退避策略：1s, 2s, 4s
"""

import os
import sys
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    from Bio import Entrez
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False

# 重试配置
MAX_RETRIES = 3
INITIAL_BACKOFF_S = 1


def _retry_with_backoff(func, *args, **kwargs):
    """
    指数退避重试装饰器

    Args:
        func: 要重试的函数
        *args, **kwargs: 函数参数

    Returns:
        函数返回值

    Raises:
        最后一次尝试的异常
    """
    last_exception = None

    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < MAX_RETRIES - 1:
                backoff_s = INITIAL_BACKOFF_S * (2 ** attempt)
                print(f"⚠️ PubMed API 调用失败 (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                print(f"   等待 {backoff_s}s 后重试...")
                time.sleep(backoff_s)
            else:
                print(f"❌ PubMed API 调用失败，已达最大重试次数")

    raise last_exception


def search_medical_db(query: str, source: str = 'pubmed', max_results: int = 10) -> str:
    """
    检索医疗数据库（PubMed 等）

    Args:
        query: 检索关键词
        source: 数据源（目前仅支持 'pubmed'）
        max_results: 最大返回结果数

    Returns:
        格式化的检索结果（标题 + 摘要）或错误信息
    """
    try:
        # 检查 Biopython 是否可用
        if not BIOPYTHON_AVAILABLE:
            return "医疗数据库检索失败: Biopython 未安装，请运行 'pip install biopython'"

        # 仅支持 PubMed
        if source.lower() != 'pubmed':
            return f"医疗数据库检索失败: 不支持的数据源 '{source}'，目前仅支持 'pubmed'"

        # 设置 NCBI Email（必需）
        email = os.getenv("NCBI_EMAIL")
        if not email:
            return "医疗数据库检索失败: 未设置 NCBI_EMAIL 环境变量"

        Entrez.email = email

        # 执行检索（带重试）
        def _search():
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort="relevance"
            )
            results = Entrez.read(handle)
            handle.close()
            return results

        search_results = _retry_with_backoff(_search)
        id_list = search_results.get("IdList", [])

        if not id_list:
            return f"医疗数据库检索结果为空: 关键词 '{query}' 未找到相关文献"

        # 获取文章摘要（带重试）
        def _fetch():
            handle = Entrez.efetch(
                db="pubmed",
                id=id_list,
                rettype="abstract",
                retmode="xml"
            )
            articles = Entrez.read(handle)
            handle.close()
            return articles

        articles = _retry_with_backoff(_fetch)

        # 格式化输出
        results = []
        for i, article in enumerate(articles['PubmedArticle'][:max_results], 1):
            try:
                medline = article['MedlineCitation']
                pmid = str(medline['PMID'])
                title = medline['Article'].get('ArticleTitle', '无标题')

                # 提取摘要
                abstract_parts = medline['Article'].get('Abstract', {}).get('AbstractText', [])
                if abstract_parts:
                    abstract = ' '.join(str(part) for part in abstract_parts)
                else:
                    abstract = '无摘要'

                # 截断摘要至 500 字符
                if len(abstract) > 500:
                    abstract = abstract[:500] + '...'

                results.append(f"[{i}] PMID: {pmid}\n标题: {title}\n摘要: {abstract}\n")

            except Exception as e:
                results.append(f"[{i}] 解析文章失败: {str(e)}\n")

        return '\n'.join(results)

    except Exception as e:
        return f"医疗数据库检索失败: {source} - {type(e).__name__}: {str(e)}"


def search_medical_db_json(query: str, source: str = 'pubmed', max_results: int = 10) -> list:
    """
    检索医疗数据库，返回结构化 JSON 列表（每条文献为独立对象）

    Returns:
        list of dicts with keys: pmid, title, abstract, url
    """
    if not BIOPYTHON_AVAILABLE:
        return []

    if source.lower() != 'pubmed':
        return []

    email = os.getenv("NCBI_EMAIL")
    if not email:
        return []

    try:
        Entrez.email = email

        search_handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results, sort="relevance")
        search_results = Entrez.read(search_handle)
        search_handle.close()

        id_list = search_results.get("IdList", [])
        if not id_list:
            return []

        fetch_handle = Entrez.efetch(db="pubmed", id=id_list, rettype="abstract", retmode="xml")
        articles = Entrez.read(fetch_handle)
        fetch_handle.close()

        results = []
        for article in articles['PubmedArticle'][:max_results]:
            try:
                medline = article['MedlineCitation']
                pmid = str(medline['PMID'])
                title = str(medline['Article'].get('ArticleTitle', ''))

                abstract_parts = medline['Article'].get('Abstract', {}).get('AbstractText', [])
                abstract = ' '.join(str(p) for p in abstract_parts) if abstract_parts else ''

                # 提取出版日期
                pub_date = ''
                try:
                    pd = medline['Article']['Journal']['JournalIssue']['PubDate']
                    year = str(pd.get('Year', ''))
                    month = str(pd.get('Month', ''))
                    day = str(pd.get('Day', ''))
                    if year:
                        pub_date = '-'.join(filter(None, [year, month.zfill(2) if month.isdigit() else month, day.zfill(2) if day.isdigit() else day]))
                    elif 'MedlineDate' in pd:
                        pub_date = str(pd['MedlineDate'])[:7]  # e.g. "2024 Jan-Feb" -> "2024 Ja"
                except Exception:
                    pass

                # 提取第一作者机构（含国别信息）
                affiliation = ''
                try:
                    authors = medline['Article'].get('AuthorList', [])
                    for author in authors:
                        aff_list = author.get('AffiliationInfo', [])
                        if aff_list:
                            affiliation = str(aff_list[0].get('Affiliation', ''))
                            break
                except Exception:
                    pass

                results.append({
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract,
                    "pub_date": pub_date,
                    "affiliation": affiliation,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
            except Exception:
                continue

        return results

    except Exception:
        return []


if __name__ == "__main__":
    # 测试用例
    test_query = "PROTAC protein degradation"
    print(f"正在检索: {test_query}")
    result = search_medical_db(test_query, max_results=3)
    print(result)


# ============================================================================
# Deep COI Parsing（深度利益冲突解析）
# ============================================================================

def extract_coi_from_pubmed(query: str, max_results: int = 20) -> Dict[str, any]:
    """
    深度解析 PubMed 文献中的利益冲突声明（Conflicts of Interest）

    策略：
    1. 搜索相关文献
    2. 从摘要和可用字段中提取 COI 相关信息
    3. 使用正则匹配提取专利号、企业授权、Startup 项目
    4. 当 general_web_search 返回空时，强制触发此模式

    Args:
        query: 搜索关键词（药物名称、靶点等）
        max_results: 最大文献数

    Returns:
        包含 COI 信息的字典
    """
    if not BIOPYTHON_AVAILABLE:
        return {
            "status": "error",
            "error": "Biopython not available",
            "coi_findings": []
        }

    email = os.getenv("NCBI_EMAIL")
    if not email:
        return {
            "status": "error",
            "error": "NCBI_EMAIL not set",
            "coi_findings": []
        }

    try:
        Entrez.email = email

        # 搜索文献
        search_handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_results,
            sort="relevance"
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()

        id_list = search_results.get("IdList", [])
        if not id_list:
            return {
                "status": "no_results",
                "message": f"未找到与 '{query}' 相关的文献",
                "coi_findings": []
            }

        # 获取文章详细信息
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=id_list,
            rettype="abstract",
            retmode="xml"
        )
        articles = Entrez.read(fetch_handle)
        fetch_handle.close()

        # 专利号正则表达式
        patent_patterns = {
            'WO': r'\b(WO\s?/?\s?\d{4}\s?/?\s?\d{6})\b',  # WO/2024/123456 or WO2024123456
            'US': r'\b(US\s?\d{7,13}[A-Z]\d?)\b',          # US20240182490A1 (支持 7-13 位数字)
            'CN': r'\b(CN\s?\d{9}[A-Z])\b',                # CN114269365A
            'JP': r'\b(JP\s?\d{7,10}[A-Z]?)\b',            # JP2023123456A
            'EP': r'\b(EP\s?\d{7}[A-Z]\d?)\b',             # EP1234567A1
        }

        # 企业授权关键词
        company_keywords = [
            r'licensed\s+to\s+(\w+(?:\s+\w+){0,3})',
            r'sponsored\s+by\s+(\w+(?:\s+\w+){0,3})',
            r'funded\s+by\s+(\w+(?:\s+\w+){0,3})',
            r'collaboration\s+with\s+(\w+(?:\s+\w+){0,3})',
            r'employee\s+of\s+(\w+(?:\s+\w+){0,3})',
            r'consultant\s+for\s+(\w+(?:\s+\w+){0,3})',
            r'stock\s+in\s+(\w+(?:\s+\w+){0,3})',
            r'equity\s+in\s+(\w+(?:\s+\w+){0,3})',
        ]

        coi_findings = []

        for article in articles['PubmedArticle'][:max_results]:
            try:
                medline = article['MedlineCitation']
                pmid = str(medline['PMID'])
                title = str(medline['Article'].get('ArticleTitle', ''))

                # 提取摘要
                abstract_parts = medline['Article'].get('Abstract', {}).get('AbstractText', [])
                abstract = ' '.join(str(p) for p in abstract_parts) if abstract_parts else ''

                # 合并文本用于 COI 分析
                full_text = f"{title} {abstract}"

                # 提取专利号
                patents_found = []
                for patent_type, pattern in patent_patterns.items():
                    matches = re.findall(pattern, full_text, re.IGNORECASE)
                    for match in matches:
                        # 清理空格
                        clean_patent = re.sub(r'\s+', '', match).upper()
                        patents_found.append({
                            "type": patent_type,
                            "number": clean_patent,
                            "context": _extract_context_coi(full_text, match)
                        })

                # 提取企业授权信息
                companies_found = []
                for pattern in company_keywords:
                    matches = re.findall(pattern, full_text, re.IGNORECASE)
                    for match in matches:
                        companies_found.append({
                            "company": match.strip(),
                            "context": _extract_context_coi(full_text, match)
                        })

                # 只保存有 COI 信息的文献
                if patents_found or companies_found:
                    coi_findings.append({
                        "pmid": pmid,
                        "title": title[:150],
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "patents": patents_found,
                        "companies": companies_found,
                        "coi_score": len(patents_found) + len(companies_found)  # 简单评分
                    })

            except Exception as e:
                continue

        # 按 COI 分数排序
        coi_findings.sort(key=lambda x: x['coi_score'], reverse=True)

        return {
            "status": "success",
            "query": query,
            "articles_searched": len(articles['PubmedArticle']),
            "coi_findings_count": len(coi_findings),
            "coi_findings": coi_findings
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"{type(e).__name__}: {str(e)}",
            "coi_findings": []
        }


def _extract_context_coi(text: str, keyword: str, context_chars: int = 100) -> str:
    """提取关键词周围的上下文"""
    try:
        idx = text.upper().find(keyword.upper())
        if idx == -1:
            return ""

        start = max(0, idx - context_chars)
        end = min(len(text), idx + len(keyword) + context_chars)

        context = text[start:end]
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."

        return context.strip()
    except:
        return ""


def search_with_coi_fallback(query: str, max_results: int = 20) -> str:
    """
    带 COI 回退的搜索策略

    当 general_web_search 返回空时，强制触发 Deep COI Parsing
    通过学术论文的作者利益关联反推隐藏的 Startup 项目

    Args:
        query: 搜索关键词
        max_results: 最大结果数

    Returns:
        格式化的 COI 分析结果
    """
    print(f"🔍 执行 Deep COI Parsing: {query}")

    result = extract_coi_from_pubmed(query, max_results=max_results)

    if result['status'] == 'error':
        return f"""Deep COI Parsing 失败

查询: {query}
错误: {result.get('error', 'Unknown error')}

建议：检查 NCBI_EMAIL 环境变量和网络连接
"""

    if result['coi_findings_count'] == 0:
        return f"""Deep COI Parsing 未找到利益冲突信息

查询: {query}
搜索文献数: {result['articles_searched']}
找到 COI 信息: 0

建议：
1. 尝试更具体的药物名称或靶点
2. 搜索相关综述文献（review）
3. 使用药物代号（如 ARV-471）而非通用名
"""

    # 格式化输出
    output = [
        f"=== Deep COI Parsing 结果 ===",
        f"查询: {query}",
        f"搜索文献数: {result['articles_searched']}",
        f"找到 COI 信息: {result['coi_findings_count']}",
        "",
        "利益冲突发现（按相关性排序）："
    ]

    for i, finding in enumerate(result['coi_findings'][:10], 1):
        output.append(f"\n{i}. PMID {finding['pmid']} (COI Score: {finding['coi_score']})")
        output.append(f"   标题: {finding['title']}")
        output.append(f"   链接: {finding['url']}")

        if finding['patents']:
            output.append(f"   📄 专利号 ({len(finding['patents'])}):")
            for patent in finding['patents'][:5]:
                output.append(f"      • {patent['number']} ({patent['type']})")
                if patent.get('context'):
                    output.append(f"        上下文: {patent['context'][:150]}")

        if finding['companies']:
            output.append(f"   🏢 企业关联 ({len(finding['companies'])}):")
            for company in finding['companies'][:5]:
                output.append(f"      • {company['company']}")
                if company.get('context'):
                    output.append(f"        上下文: {company['context'][:150]}")

    output.append("\n" + "="*60)
    output.append("💡 Deep COI Parsing 策略：")
    output.append("1. 专利号可用于 search_patent_by_number() 获取详情")
    output.append("2. 企业关联可用于反推 Startup 项目和授权信息")
    output.append("3. 访问全文获取完整的 Conflicts of Interest 声明")

    return "\n".join(output)
