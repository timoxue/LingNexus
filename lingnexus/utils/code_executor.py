"""
代码执行工具
用于提取和执行 Agent 生成的代码

支持两种执行方式：
1. AgentScope 内置工具（推荐）：使用 execute_python_code，更安全可靠
2. exec() 方式（备用）：直接在当前进程执行，支持工作目录控制
"""

import re
import sys
import io
import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

# Windows 编码修复：设置环境变量，确保子进程使用 UTF-8 编码
if sys.platform == 'win32':
    # 确保子进程使用 UTF-8 编码
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    os.environ.setdefault('PYTHONLEGACYWINDOWSSTDIO', '0')


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


def _parse_agentscope_response(tool_response) -> Dict[str, Any]:
    """
    解析 AgentScope ToolResponse 的 XML 格式结果
    
    Args:
        tool_response: AgentScope ToolResponse 对象
    
    Returns:
        包含执行结果的字典
    """
    try:
        content = tool_response.content
        if isinstance(content, list):
            # 提取文本内容
            text_content = ''
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'text':
                    text_content = item.get('text', '')
                    break
        else:
            text_content = str(content)
        
        # 解析 XML 标签
        returncode_match = re.search(r'<returncode>(\d+)</returncode>', text_content)
        stdout_match = re.search(r'<stdout>(.*?)</stdout>', text_content, re.DOTALL)
        stderr_match = re.search(r'<stderr>(.*?)</stderr>', text_content, re.DOTALL)
        
        returncode = int(returncode_match.group(1)) if returncode_match else 1
        stdout = stdout_match.group(1) if stdout_match else ''
        stderr = stderr_match.group(1) if stderr_match else ''
        
        # 清理输出（移除 Windows 的 \r）
        stdout = stdout.replace('\r\n', '\n').replace('\r', '\n').strip()
        stderr = stderr.replace('\r\n', '\n').replace('\r', '\n').strip()
        
        return {
            'success': returncode == 0,
            'output': stdout,
            'error': stderr if stderr else '',
            'returncode': returncode,
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': f'解析 AgentScope 响应失败: {e}',
            'returncode': 1,
        }


async def execute_python_code_with_agentscope(
    code: str,
    working_dir: Optional[Path] = None,
    timeout: float = 300,
) -> Dict[str, Any]:
    """
    使用 AgentScope 内置工具执行 Python 代码（异步）
    
    优势：
    - 使用官方工具，更可靠
    - 支持超时设置
    - 在临时文件中执行，更安全
    
    注意：
    - 这是异步函数
    - 如果指定了 working_dir，会在代码开头添加目录切换
    
    Args:
        code: 要执行的 Python 代码
        working_dir: 工作目录（通过代码切换实现）
        timeout: 超时时间（秒），默认 300 秒
    
    Returns:
        包含执行结果的字典
    """
    try:
        from agentscope.tool import execute_python_code as agentscope_execute
    except ImportError:
        return {
            'success': False,
            'output': '',
            'error': 'AgentScope execute_python_code 工具不可用，请确保已安装 AgentScope',
            'returncode': 1,
        }
    
    try:
        # 如果指定了工作目录，在代码开头添加目录切换
        if working_dir:
            working_dir = Path(working_dir).resolve()
            # 转义路径中的反斜杠和引号
            dir_str = str(working_dir).replace('\\', '\\\\').replace("'", "\\'")
            code = f"""
import os
os.chdir(r"{dir_str}")
{code}
"""
        
        # 设置环境变量，确保子进程使用 UTF-8 编码（Windows 兼容）
        import os as os_module
        original_env = os_module.environ.copy()
        try:
            # 设置环境变量，强制使用 UTF-8
            os_module.environ['PYTHONIOENCODING'] = 'utf-8'
            if sys.platform == 'win32':
                # Windows 特定设置
                os_module.environ['PYTHONLEGACYWINDOWSSTDIO'] = '0'
            
            # 调用 AgentScope 内置工具
            tool_response = await agentscope_execute(code, timeout=timeout)
        finally:
            # 恢复原始环境变量
            os_module.environ.clear()
            os_module.environ.update(original_env)
        
        # 解析返回结果
        result = _parse_agentscope_response(tool_response)
        return result
        
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': f'执行代码时出错: {str(e)}',
            'returncode': 1,
        }


def execute_python_code(
    code: str, 
    working_dir: Optional[Path] = None,
    use_agentscope: bool = True,
    timeout: float = 300,
) -> Dict[str, Any]:
    """
    执行 Python 代码
    
    支持两种执行方式：
    1. AgentScope 内置工具（推荐）：更安全可靠，支持超时
    2. exec() 方式（备用）：直接执行，支持工作目录控制
    
    Args:
        code: 要执行的 Python 代码
        working_dir: 工作目录（代码执行时的当前目录）
        use_agentscope: 是否优先使用 AgentScope 内置工具（默认 True）
        timeout: 超时时间（秒），仅在使用 AgentScope 工具时有效
    
    Returns:
        包含执行结果的字典：
        - success: 是否成功
        - output: 标准输出
        - error: 错误信息
        - returncode: 返回码（使用 AgentScope 工具时）
        - files_created: 创建的文件列表（使用 exec() 时）
    """
    # 优先使用 AgentScope 内置工具
    if use_agentscope:
        try:
            # 在同步函数中调用异步函数
            return asyncio.run(execute_python_code_with_agentscope(code, working_dir, timeout))
        except Exception as e:
            # 如果 AgentScope 工具失败，回退到 exec() 方式
            # 注意：这里不打印错误，让 exec() 方式作为备用
            pass
    
    # 使用原有的 exec() 方式（备用）
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


def extract_and_execute_code(
    agent_response: str, 
    working_dir: Optional[Path] = None,
    use_agentscope: bool = True,
    timeout: float = 300,
) -> Dict[str, Any]:
    """
    从 Agent 响应中提取代码并执行（同步版本）
    
    Args:
        agent_response: Agent 的响应文本
        working_dir: 工作目录
        use_agentscope: 是否使用 AgentScope 内置工具（默认 True）
        timeout: 超时时间（秒），仅在使用 AgentScope 工具时有效
    
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
    
    result = execute_python_code(code, working_dir, use_agentscope, timeout)
    result['code'] = code
    
    return result


async def extract_and_execute_code_async(
    agent_response: str,
    working_dir: Optional[Path] = None,
    use_agentscope: bool = True,
    timeout: float = 300,
) -> Dict[str, Any]:
    """
    从 Agent 响应中提取代码并执行（异步版本）
    
    在异步环境中使用此函数可以获得更好的性能。
    
    Args:
        agent_response: Agent 的响应文本
        working_dir: 工作目录
        use_agentscope: 是否使用 AgentScope 内置工具（默认 True）
        timeout: 超时时间（秒），仅在使用 AgentScope 工具时有效
    
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
    
    if use_agentscope:
        result = await execute_python_code_with_agentscope(code, working_dir, timeout)
    else:
        # 使用 exec() 方式（在线程池中执行）
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: execute_python_code(code, working_dir, use_agentscope=False)
        )
    
    result['code'] = code
    return result

