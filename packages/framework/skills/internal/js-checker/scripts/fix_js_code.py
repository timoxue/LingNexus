#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 JavaScript 代码中的常见问题
- 全角符号（中文标点符号）
- 编码问题
- 常见语法错误
"""

import re
import json
import sys

# 全角符号到半角符号的映射
FULLWIDTH_TO_HALFWIDTH = {
    # 标点符号
    "，": ",",
    "。": ".",
    "！": "!",
    "？": "?",
    "：": ":",
    "；": ";",
    "（": "(",
    "）": ")",
    "【": "[",
    "】": "]",
    "「": "'",
    "」": "'",
    "『": '"',
    "』": '"',
    "、": ",",
    "…": "...",
    "—": "-",
    "–": "-",
    # 引号
    """: '"',
    """: '"',
    "'": "'",
    "'": "'",
    # 空格
    "　": " ",  # 全角空格
}


def fix_fullwidth_chars(code: str) -> tuple[str, list]:
    """
    修复全角符号
    
    Args:
        code: JavaScript 代码
    
    Returns:
        tuple: (修复后的代码, 修复列表)
    """
    fixes = []
    lines = code.split("\n")
    fixed_lines = []
    
    for line_num, line in enumerate(lines, 1):
        original_line = line
        fixed_line = line
        
        # 替换全角符号
        for fullwidth, halfwidth in FULLWIDTH_TO_HALFWIDTH.items():
            if fullwidth in fixed_line:
                count = fixed_line.count(fullwidth)
                fixed_line = fixed_line.replace(fullwidth, halfwidth)
                fixes.append({
                    "type": "fullwidth_char",
                    "line": line_num,
                    "original": fullwidth,
                    "fixed": halfwidth,
                    "count": count,
                })
        
        fixed_lines.append(fixed_line)
    
    return "\n".join(fixed_lines), fixes


def fix_encoding_issues(code: str) -> tuple[str, list]:
    """
    修复编码问题
    
    Args:
        code: JavaScript 代码
    
    Returns:
        tuple: (修复后的代码, 修复列表)
    """
    fixes = []
    
    # 检查并修复常见的编码问题
    # 这里可以添加更多编码修复逻辑
    
    return code, fixes


def fix_common_syntax_errors(code: str) -> tuple[str, list]:
    """
    修复常见的语法错误
    
    Args:
        code: JavaScript 代码
    
    Returns:
        tuple: (修复后的代码, 修复列表)
    """
    fixes = []
    fixed_code = code
    
    # 修复常见的语法错误模式
    # 例如：修复多余的分号、括号等
    
    return fixed_code, fixes


def fix_js_code(js_code: str) -> dict:
    """
    修复 JavaScript 代码中的所有问题
    
    Args:
        js_code: JavaScript 代码字符串
    
    Returns:
        dict: 包含修复结果的字典
    """
    fixes_applied = []
    fixed_code = js_code
    
    # 1. 修复全角符号
    fixed_code, fullwidth_fixes = fix_fullwidth_chars(fixed_code)
    fixes_applied.extend(fullwidth_fixes)
    
    # 2. 修复编码问题
    fixed_code, encoding_fixes = fix_encoding_issues(fixed_code)
    fixes_applied.extend(encoding_fixes)
    
    # 3. 修复常见语法错误
    fixed_code, syntax_fixes = fix_common_syntax_errors(fixed_code)
    fixes_applied.extend(syntax_fixes)
    
    return {
        "fixed_code": fixed_code,
        "fixes_applied": fixes_applied,
        "fixes_count": len(fixes_applied),
        "original_code": js_code,
        "changed": fixed_code != js_code,
    }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python fix_js_code.py <js_code>")
        print("或从标准输入读取: python fix_js_code.py -")
        sys.exit(1)
    
    if sys.argv[1] == "-":
        # 从标准输入读取
        js_code = sys.stdin.read()
    else:
        # 从文件读取
        from pathlib import Path
        js_code = Path(sys.argv[1]).read_text(encoding="utf-8")
    
    result = fix_js_code(js_code)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()


