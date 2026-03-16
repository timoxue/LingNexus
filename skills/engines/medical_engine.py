"""
L1 引擎层：医疗数据库检索引擎
封装 OpenClaw-Medical-Skills 库的 PubMed API
安全策略：异常捕获 + 熔断保护，返回错误字符串
"""

import os
import sys
from pathlib import Path

try:
    from Bio import Entrez
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False


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

        # 执行检索
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
            return f"医疗数据库检索结果为空: 关键词 '{query}' 未找到相关文献"

        # 获取文章摘要
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=id_list,
            rettype="abstract",
            retmode="xml"
        )
        articles = Entrez.read(fetch_handle)
        fetch_handle.close()

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


if __name__ == "__main__":
    # 测试用例
    test_query = "PROTAC protein degradation"
    print(f"正在检索: {test_query}")
    result = search_medical_db(test_query, max_results=3)
    print(result)
