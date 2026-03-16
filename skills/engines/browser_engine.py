"""
L1 引擎层：浏览器引擎（基于 OpenClaw Browser）
封装 OpenClaw 原生 browser 工具
安全策略：15 秒超时 + 异常捕获，返回错误字符串
"""

import subprocess
import sys
import json
import os
from pathlib import Path

# 导入 L2 清洗器
sys.path.append(str(Path(__file__).parent.parent))
from scrapers.data_cleaner import clean_html_to_text


def fetch_webpage_content(url: str, timeout: int = 15) -> str:
    """
    抓取网页内容并清洗为纯文本（使用 OpenClaw Browser）

    Args:
        url: 目标网页 URL
        timeout: 超时时间（秒），默认 15 秒

    Returns:
        清洗后的纯文本或错误信息
    """
    try:
        # 设置环境变量
        env = os.environ.copy()
        env['DISPLAY'] = ':99'

        # 步骤 1: 打开网页
        open_result = subprocess.run(
            ['runuser', '-u', 'node', '--', 'node', '/app/openclaw.mjs', 'browser', 'open', url],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env
        )

        if open_result.returncode != 0:
            error_msg = open_result.stderr.strip() if open_result.stderr else "未知错误"
            return f"网页打开失败: {url} - {error_msg}"

        # 步骤 2: 获取页面 HTML
        # 使用 evaluate 命令执行 JavaScript 获取完整 HTML
        eval_result = subprocess.run(
            ['runuser', '-u', 'node', '--', 'node', '/app/openclaw.mjs', 'browser', 'evaluate',
             '--fn', 'document.documentElement.outerHTML'],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env
        )

        if eval_result.returncode != 0:
            error_msg = eval_result.stderr.strip() if eval_result.stderr else "未知错误"
            return f"网页内容获取失败: {url} - {error_msg}"

        # 获取 HTML 内容（OpenClaw 返回的是 JSON 字符串）
        html_content = eval_result.stdout.strip()

        # 尝试解析 JSON（如果是 JSON 格式）
        try:
            if html_content.startswith('"') and html_content.endswith('"'):
                html_content = json.loads(html_content)
        except:
            pass  # 如果不是 JSON，保持原样

        if not html_content or len(html_content) < 50:
            return f"网页抓取失败: {url} - 返回内容为空或过短"

        # 调用 L2 清洗器
        cleaned_text = clean_html_to_text(html_content)

        return cleaned_text

    except subprocess.TimeoutExpired:
        return f"网页抓取超时: {url} - 超过 {timeout} 秒未响应"

    except FileNotFoundError:
        return f"网页抓取失败: OpenClaw 命令未找到，请检查环境"

    except Exception as e:
        return f"网页抓取异常: {url} - {type(e).__name__}: {str(e)}"


if __name__ == "__main__":
    # 测试用例
    test_url = "https://example.com"
    print(f"正在抓取: {test_url}")
    result = fetch_webpage_content(test_url)
    print(result[:500])  # 只打印前 500 字符
