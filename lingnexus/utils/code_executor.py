"""
代码执行工具
用于提取和执行 Agent 生成的代码
"""

import re
import sys
import io
from pathlib import Path
from typing import Optional, Dict, Any


def extract_python_code(text: str) -> Optional[str]:
    """
    从文本中提取 Python 代码块
    
    Args:
        text: 包含代码的文本
    
    Returns:
        提取的 Python 代码，如果未找到则返回 None
    """
    # 匹配 ```python ... ``` 或 ``` ... ```
    patterns = [
        r'```python\s*\n(.*?)```',
        r'```\s*\n(.*?)```',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            # 返回最后一个代码块（通常是最完整的）
            return matches[-1].strip()
    
    return None


def execute_python_code(code: str, working_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    执行 Python 代码
    
    Args:
        code: 要执行的 Python 代码
        working_dir: 工作目录（代码执行时的当前目录）
    
    Returns:
        包含执行结果的字典：
        - success: 是否成功
        - output: 标准输出
        - error: 错误信息
        - files_created: 创建的文件列表
    """
    result = {
        'success': False,
        'output': '',
        'error': '',
        'files_created': [],
    }
    
    # 保存原始工作目录
    original_dir = Path.cwd()
    
    try:
        # 切换到指定工作目录
        if working_dir:
            working_dir = Path(working_dir)
            working_dir.mkdir(parents=True, exist_ok=True)
            os.chdir(str(working_dir))
        
        # 捕获标准输出和错误
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # 保存原始标准输出和错误
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # 准备执行环境，包含常用模块
            exec_globals = {
                '__name__': '__main__',
                '__builtins__': __builtins__,
                # 添加常用模块到执行环境
                'os': __import__('os'),
                'sys': __import__('sys'),
                'Path': Path,
                'datetime': __import__('datetime'),
            }
            
            # 执行代码
            exec(code, exec_globals)
            
            result['success'] = True
            result['output'] = stdout_capture.getvalue()
            
        except Exception as e:
            result['error'] = str(e)
            result['output'] = stdout_capture.getvalue()
            result['error'] += '\n' + stderr_capture.getvalue()
        
        finally:
            # 恢复标准输出和错误
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        # 检查创建的文件（简单方法：检查当前目录的新文件）
        if working_dir:
            # 这里可以添加更复杂的文件检测逻辑
            pass
        
    except Exception as e:
        result['error'] = str(e)
    
    finally:
        # 恢复原始工作目录
        try:
            os.chdir(str(original_dir))
        except Exception:
            pass  # 忽略恢复目录时的错误
    
    return result


def extract_and_execute_code(agent_response: str, working_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    从 Agent 响应中提取代码并执行
    
    Args:
        agent_response: Agent 的响应文本
        working_dir: 工作目录
    
    Returns:
        执行结果字典
    """
    code = extract_python_code(agent_response)
    
    if not code:
        return {
            'success': False,
            'error': '未找到 Python 代码块',
            'code': None,
        }
    
    result = execute_python_code(code, working_dir)
    result['code'] = code
    
    return result

