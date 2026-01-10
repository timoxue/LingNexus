#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查本地 Node.js 版本
"""

import subprocess
import sys
import json
from pathlib import Path

def check_node_version():
    """
    检查本地 Node.js 版本
    
    Returns:
        dict: 包含版本信息的字典
    """
    result = {
        "installed": False,
        "version": None,
        "major": None,
        "minor": None,
        "patch": None,
        "meets_requirement": False,
        "error": None,
    }
    
    try:
        # 检查 Node.js 是否安装
        # 使用 errors='replace' 处理编码错误（Windows 系统可能输出 GBK 编码）
        process = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # 处理编码错误
            timeout=5,
        )
        
        if process.returncode != 0:
            result["error"] = f"Node.js 未安装或无法访问: {process.stderr}"
            return result
        
        # 解析版本号 (格式: v18.17.0)
        version_str = process.stdout.strip()
        if version_str.startswith("v"):
            version_str = version_str[1:]
        
        version_parts = version_str.split(".")
        result["installed"] = True
        result["version"] = version_str
        
        if len(version_parts) >= 1:
            result["major"] = int(version_parts[0])
        if len(version_parts) >= 2:
            result["minor"] = int(version_parts[1])
        if len(version_parts) >= 3:
            result["patch"] = int(version_parts[2])
        
        # 检查是否满足最低要求 (>= 14.0.0)
        if result["major"] is not None:
            result["meets_requirement"] = result["major"] >= 14
        
    except FileNotFoundError:
        result["error"] = "Node.js 未安装，请先安装 Node.js"
    except subprocess.TimeoutExpired:
        result["error"] = "检查 Node.js 版本超时"
    except Exception as e:
        result["error"] = f"检查 Node.js 版本时出错: {str(e)}"
    
    return result


def main():
    """主函数"""
    result = check_node_version()
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

