#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的 JavaScript 代码检查和修复流程
"""

import json
import sys
from pathlib import Path

# 导入其他脚本的功能
from check_node_version import check_node_version
from check_js_syntax import check_js_syntax
from fix_js_code import fix_js_code
from validate_js import validate_js


def check_and_fix_js(js_code: str) -> dict:
    """
    完整的检查和修复流程
    
    Args:
        js_code: JavaScript 代码字符串
    
    Returns:
        dict: 包含完整检查结果的字典
    """
    result = {
        "node_version": None,
        "syntax_ok": False,
        "fixed_code": js_code,
        "validation_ok": False,
        "execute_command": None,
        "fixes_applied": [],
        "errors": [],
        "warnings": [],
    }
    
    # 1. 检查 Node.js 版本
    node_version_result = check_node_version()
    result["node_version"] = node_version_result
    
    if not node_version_result.get("installed"):
        result["errors"].append(f"Node.js 未安装: {node_version_result.get('error')}")
        return result
    
    if not node_version_result.get("meets_requirement"):
        result["warnings"].append(
            f"Node.js 版本 {node_version_result.get('version')} 可能不支持某些语法特性"
        )
    
    # 2. 修复代码
    fix_result = fix_js_code(js_code)
    result["fixed_code"] = fix_result["fixed_code"]
    result["fixes_applied"] = fix_result["fixes_applied"]
    
    # 3. 检查修复后的代码语法
    syntax_result = check_js_syntax(fix_result["fixed_code"], node_version_result)
    result["syntax_ok"] = syntax_result["valid"]
    
    if not syntax_result["valid"]:
        result["errors"].extend(syntax_result["errors"])
    
    if syntax_result.get("warnings"):
        result["warnings"].extend(syntax_result["warnings"])
    
    # 4. 验证代码可执行性
    if syntax_result["valid"]:
        validation_result = validate_js(fix_result["fixed_code"])
        result["validation_ok"] = validation_result["valid"] and validation_result["executable"]
        
        if not validation_result["valid"]:
            result["errors"].extend(validation_result["errors"])
    
    # 5. 生成执行命令
    if result["validation_ok"]:
        # 转义代码中的引号和特殊字符
        escaped_code = fix_result["fixed_code"].replace('"', '\\"').replace('\n', '\\n')
        result["execute_command"] = f'node -e "{escaped_code}"'
    elif result["syntax_ok"]:
        # 语法正确但执行失败，仍然提供执行命令
        escaped_code = fix_result["fixed_code"].replace('"', '\\"').replace('\n', '\\n')
        result["execute_command"] = f'node -e "{escaped_code}"'
        result["warnings"].append("代码语法正确，但执行验证失败，请检查运行时错误")
    
    return result


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python check_and_fix_js.py <js_code>")
        print("或从标准输入读取: python check_and_fix_js.py -")
        sys.exit(1)
    
    if sys.argv[1] == "-":
        # 从标准输入读取
        js_code = sys.stdin.read()
    else:
        # 从文件读取
        js_code = Path(sys.argv[1]).read_text(encoding="utf-8")
    
    result = check_and_fix_js(js_code)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()


