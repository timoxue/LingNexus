#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 JavaScript 代码语法
"""

import subprocess
import json
import sys
import re
import tempfile
from pathlib import Path


def check_js_syntax(js_code: str, node_version: dict = None) -> dict:
    """
    检查 JavaScript 代码语法
    
    Args:
        js_code: JavaScript 代码字符串
        node_version: Node.js 版本信息（可选）
    
    Returns:
        dict: 包含检查结果的字典
    """
    result = {
        "valid": False,
        "errors": [],
        "warnings": [],
        "syntax_features": [],
        "error": None,
    }
    
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(js_code)
            temp_file = f.name
        
        try:
            # 使用 node --check 检查语法
            # 使用 errors='replace' 处理编码错误（Windows 系统可能输出 GBK 编码）
            process = subprocess.run(
                ["node", "--check", temp_file],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # 处理编码错误
                timeout=10,
            )
            
            if process.returncode == 0:
                result["valid"] = True
            else:
                # 解析错误信息
                error_output = process.stderr.strip()
                result["errors"].append(error_output)
                result["error"] = error_output
            
            # 检测语法特性（简单检测）
            syntax_features = detect_syntax_features(js_code)
            result["syntax_features"] = syntax_features
            
            # 检查语法特性兼容性（如果提供了 node_version）
            if node_version and node_version.get("major"):
                compatibility = check_feature_compatibility(syntax_features, node_version["major"])
                if not compatibility["all_supported"]:
                    result["warnings"].extend(compatibility["unsupported_features"])
        
        finally:
            # 删除临时文件
            Path(temp_file).unlink()
    
    except FileNotFoundError:
        result["error"] = "Node.js 未安装，无法检查语法"
    except subprocess.TimeoutExpired:
        result["error"] = "语法检查超时"
    except Exception as e:
        result["error"] = f"检查语法时出错: {str(e)}"
    
    return result


def detect_syntax_features(js_code: str) -> list:
    """
    检测代码中使用的语法特性
    
    Args:
        js_code: JavaScript 代码
    
    Returns:
        list: 语法特性列表
    """
    features = []
    
    # 检测 ES6+ 特性
    if re.search(r"=>\s*", js_code):
        features.append("arrow-functions")
    
    if re.search(r"async\s+function|await\s+", js_code):
        features.append("async-await")
    
    if re.search(r"const\s+|let\s+", js_code):
        features.append("let-const")
    
    if re.search(r"class\s+\w+", js_code):
        features.append("classes")
    
    if re.search(r"\.\.\.\s*\w+", js_code):
        features.append("spread-operator")
    
    if re.search(r"`[^`]*\$\{", js_code):
        features.append("template-literals")
    
    if re.search(r"import\s+.*from|export\s+", js_code):
        features.append("es-modules")
    
    return features


def check_feature_compatibility(features: list, node_major_version: int) -> dict:
    """
    检查语法特性与 Node.js 版本的兼容性
    
    Args:
        features: 语法特性列表
        node_major_version: Node.js 主版本号
    
    Returns:
        dict: 兼容性检查结果
    """
    # 特性最低版本要求
    feature_requirements = {
        "arrow-functions": 4,
        "async-await": 7,
        "let-const": 4,
        "classes": 4,
        "spread-operator": 5,
        "template-literals": 4,
        "es-modules": 12,
    }
    
    unsupported = []
    for feature in features:
        required_version = feature_requirements.get(feature, 0)
        if node_major_version < required_version:
            unsupported.append({
                "feature": feature,
                "required_version": required_version,
                "current_version": node_major_version,
            })
    
    return {
        "all_supported": len(unsupported) == 0,
        "unsupported_features": unsupported,
    }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python check_js_syntax.py <js_code>")
        print("或从标准输入读取: python check_js_syntax.py -")
        sys.exit(1)
    
    if sys.argv[1] == "-":
        # 从标准输入读取
        js_code = sys.stdin.read()
    else:
        # 从文件读取
        from pathlib import Path
        js_code = Path(sys.argv[1]).read_text(encoding="utf-8")
    
    # 可选：从环境变量或参数获取 node_version
    node_version = None
    if len(sys.argv) >= 3:
        import json
        node_version = json.loads(sys.argv[2])
    
    result = check_js_syntax(js_code, node_version)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

