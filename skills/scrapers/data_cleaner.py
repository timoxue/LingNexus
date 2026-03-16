"""
L2 解析层：HTML 清洗与文本提取
安全策略：所有异常必须捕获并返回错误字符串，绝不向上抛出
"""

from bs4 import BeautifulSoup
import re


def clean_html_to_text(html_content: str) -> str:
    """
    清洗 HTML 内容，提取纯文本

    Args:
        html_content: 原始 HTML 字符串

    Returns:
        清洗后的纯文本（最大 8000 字符）或错误信息
    """
    try:
        # 创建 BeautifulSoup 对象
        soup = BeautifulSoup(html_content, 'html.parser')

        # 移除非正文标签
        for tag in soup(['script', 'style', 'nav', 'footer', 'header',
                        'aside', 'iframe', 'noscript']):
            tag.decompose()

        # 提取纯文本
        text = soup.get_text(separator='\n', strip=True)

        # 去除多余空行（连续的换行符压缩为最多两个）
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 去除每行首尾空格
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(line for line in lines if line)

        # 硬截断至 8000 字符
        if len(text) > 8000:
            text = text[:8000] + '\n[内容已截断至 8000 字符]'

        return text

    except Exception as e:
        return f"解析失败: {type(e).__name__} - {str(e)}"


if __name__ == "__main__":
    # 测试用例
    test_html = """
    <html>
        <head><title>Test</title></head>
        <body>
            <nav>导航栏</nav>
            <header>页头</header>
            <main>
                <h1>标题</h1>
                <p>这是正文内容。</p>
                <script>alert('test');</script>
            </main>
            <footer>页脚</footer>
        </body>
    </html>
    """
    print(clean_html_to_text(test_html))
