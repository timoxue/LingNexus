#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 JavaScript 代码是否可以执行
"""

import subprocess
import json
import sys
import os
import tempfile
from pathlib import Path


def validate_js(js_code: str, timeout: int = 10) -> dict:
    """
    验证 JavaScript 代码是否可以执行

    Args:
        js_code: JavaScript 代码字符串
        timeout: 超时时间（秒）

    Returns:
        dict: 包含验证结果的字典
    """
    result = {
        "valid": False,
        "executable": False,
        "errors": [],
        "output": "",
        "returncode": None,
        "error": None,
    }

    # 获取项目根目录（向上查找包含 package.json 的目录）
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir
    for parent in [current_dir] + list(current_dir.parents):
        if (parent / "package.json").exists():
            project_root = parent
            break

    try:
        # 创建临时文件（在项目根目录下，而不是系统临时目录）
        temp_file = project_root / f"temp_{Path(__file__).stem}_{id(js_code) & 0xFFFFFFFF}.js"
        temp_file.write_text(js_code, encoding="utf-8")

        try:
            # 设置环境变量，确保 Node.js 能找到 node_modules
            env = {
                **os.environ,
                "NODE_PATH": str(project_root / "node_modules"),
            }

            # 尝试执行代码
            # 重要：设置 cwd 为项目根目录，以便找到 node_modules
            # 使用 errors='replace' 处理编码错误（Windows 系统可能输出 GBK 编码）
            process = subprocess.run(
                ["node", str(temp_file)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # 处理编码错误
                timeout=timeout,
                cwd=str(project_root),  # 设置工作目录为项目根目录
                env=env,  # 设置环境变量
            )
            
            result["returncode"] = process.returncode
            result["output"] = process.stdout.strip()
            
            if process.returncode == 0:
                result["valid"] = True
                result["executable"] = True
            else:
                # 执行失败
                error_output = process.stderr.strip()
                result["errors"].append(error_output)
                result["error"] = error_output
        
        finally:
            # 删除临时文件
            Path(temp_file).unlink()
    
    except FileNotFoundError:
        result["error"] = "Node.js 未安装，无法验证代码"
    except subprocess.TimeoutExpired:
        result["error"] = f"代码执行超时（>{timeout}秒）"
        result["errors"].append("执行超时")
    except Exception as e:
        result["error"] = f"验证代码时出错: {str(e)}"
        result["errors"].append(str(e))
    
    return result


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python validate_js.py <js_code> [timeout]")
        print("或从标准输入读取: python validate_js.py - [timeout]")
        sys.exit(1)
    
    if sys.argv[1] == "-":
        # 从标准输入读取
        js_code = sys.stdin.read()
    else:
        # 从文件读取
        from pathlib import Path
        js_code = Path(sys.argv[1]).read_text(encoding="utf-8")
    
    timeout = 10
    if len(sys.argv) >= 3:
        timeout = int(sys.argv[2])
    
    result = validate_js(js_code, timeout)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

