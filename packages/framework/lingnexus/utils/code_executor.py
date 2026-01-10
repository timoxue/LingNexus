"""
代码执行工具
用于提取和执行 Agent 生成的代码

支持两种执行方式：
1. AgentScope 内置工具（推荐）：使用 execute_python_code，更安全可靠
2. exec() 方式（备用）：直接在当前进程执行，支持工作目录控制

支持的语言：
- Python: 使用 AgentScope execute_python_code
- JavaScript: 使用 Node.js 执行
- Bash: 使用 Shell 执行
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
    # 匹配 ```python ... ``` （优先级最高）
    python_block = re.search(r'```python\s*\n(.*?)```', text, re.DOTALL)
    if python_block:
        code = python_block.group(1).strip()
        # 验证代码看起来像 Python（包含 Python 关键字或常见语句）
        if _looks_like_python(code):
            return code

    # 匹配 ``` ... ``` （仅当明确标记为 python 时）
    generic_block = re.search(r'```\s*(python)?\s*\n(.*?)```', text, re.DOTALL)
    if generic_block:
        code = generic_block.group(2).strip()
        # 验证代码看起来像 Python
        if _looks_like_python(code):
            return code

    return None


def _looks_like_python(code: str) -> bool:
    """
    验证代码看起来像 Python 代码

    Args:
        code: 代码字符串

    Returns:
        是否看起来像 Python 代码
    """
    # 快速拒绝：包含明显的非 Python 特征
    # 1. 中文标点符号（全角）
    chinese_punctuation = ['，', '。', '；', '：', '？', '！', '「', '」', '『', '』']
    if any(punct in code for punct in chinese_punctuation):
        return False

    # 2. 文本说明模式
    text_patterns = [
        r'将.*保存为',           # "将代码保存为"
        r'然后在.*运行',          # "然后在终端运行"
        r'请运行.*命令',          # "请运行以下命令"
        r'执行.*脚本',            # "执行脚本"
    ]
    for pattern in text_patterns:
        if re.search(pattern, code):
            return False

    # Python 关键字和常见模式
    python_patterns = [
        r'\bdef\s+\w+\s*\(',           # 函数定义
        r'\bclass\s+\w+\s*:',          # 类定义
        r'\bimport\s+\w+',             # import 语句
        r'\bfrom\s+\w+\s+import',      # from ... import
        r'\bprint\s*\(',               # print 函数
        r'\bif\s+__name__\s*==',       # if __name__ == "__main__"
        r'^\s*\w+\s*=\s*',             # 变量赋值（行首）
    ]

    # 检查是否至少包含一个 Python 模式
    for pattern in python_patterns:
        if re.search(pattern, code, re.MULTILINE):
            return True

    # 如果代码很短（< 50字符），更严格地检查
    if len(code) < 50:
        return any(re.search(p, code, re.MULTILINE) for p in python_patterns[:3])

    # 较长的代码假设是 Python
    return len(code) > 100


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



# ============================================================================
# 多语言代码提取和执行
# ============================================================================

def extract_javascript_code(text: str) -> Optional[str]:
    """
    从文本中提取 JavaScript 代码块

    Args:
        text: 包含代码的文本

    Returns:
        提取的 JavaScript 代码，如果未找到则返回 None
    """
    # 匹配 ```javascript ... ``` 或 ```js ... ```
    patterns = [
        r'```javascript\s*\n(.*?)```',
        r'```js\s*\n(.*?)```',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1).strip()
            # 验证代码看起来像 JavaScript
            if _looks_like_javascript(code):
                return code

    return None


def extract_bash_code(text: str) -> Optional[str]:
    """
    从文本中提取 Bash 代码块

    Args:
        text: 包含代码的文本

    Returns:
        提取的 Bash 代码，如果未找到则返回 None
    """
    # 匹配 ```bash ... ```
    pattern = r'```bash\s*\n(.*?)```'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        code = match.group(1).strip()
        # 验证代码看起来像 Bash
        if _looks_like_bash(code):
            return code

    return None


def _looks_like_javascript(code: str) -> bool:
    """
    验证代码看起来像 JavaScript 代码

    Args:
        code: 代码字符串

    Returns:
        是否看起来像 JavaScript 代码
    """
    # 快速拒绝：包含明显的非 JavaScript 特征
    chinese_punctuation = ['，', '。', '；', '：', '？', '！']
    if any(punct in code for punct in chinese_punctuation):
        return False

    # JavaScript 关键字和常见模式
    js_patterns = [
        r'\bconst\s+\w+\s*=',
        r'\blet\s+\w+\s*=',
        r'\bvar\s+\w+\s*=',
        r'\bfunction\s+\w+\s*\(',
        r'=>\s*{',  # 箭头函数
        r'\brequire\s*\(',
        r'\bconsole\.',
        r'\bexport\s+',
        r'\bimport\s+.*from',
    ]

    # 检查是否至少包含一个 JavaScript 模式
    for pattern in js_patterns:
        if re.search(pattern, code):
            return True

    # 如果代码很短（< 50字符），更严格地检查
    if len(code) < 50:
        return any(re.search(p, code) for p in js_patterns[:3])

    # 较长的代码假设是 JavaScript
    return len(code) > 80


def _looks_like_bash(code: str) -> bool:
    """
    验证代码看起来像 Bash 脚本

    Args:
        code: 代码字符串

    Returns:
        是否看起来像 Bash 脚本
    """
    # Bash 常见模式
    bash_patterns = [
        r'#!/bin/bash',
        r'#!/bin/sh',
        r'\bif\s+.*;\s*then',
        r'\bfor\s+.*\s+in',
        r'\becho\s+',
        r'\bcd\s+',
        r'\bexport\s+',
        r'\bpwd\s*',
        r'\bls\s+',
        r'\bcat\s+',
    ]

    # 检查是否至少包含一个 Bash 模式
    for pattern in bash_patterns:
        if re.search(pattern, code):
            return True

    # 如果代码很短但包含命令，也认为是 Bash
    if len(code) < 50:
        return any(re.search(p, code) for p in bash_patterns[4:])

    # 较长的代码假设是 Bash
    return len(code) > 50


def extract_code_from_text(text: str) -> Dict[str, Optional[str]]:
    """
    从文本中提取所有语言的代码块

    Args:
        text: 包含代码的文本

    Returns:
        字典，键为语言名称，值为提取的代码
        例如: {'python': '...', 'javascript': '...', 'bash': '...'}
    """
    codes = {}

    # 提取 Python 代码
    python_code = extract_python_code(text)
    if python_code:
        codes['python'] = python_code

    # 提取 JavaScript 代码
    js_code = extract_javascript_code(text)
    if js_code:
        codes['javascript'] = js_code

    # 提取 Bash 代码
    bash_code = extract_bash_code(text)
    if bash_code:
        codes['bash'] = bash_code

    return codes


async def execute_javascript_code(
    code: str,
    timeout: float = 30,
    keep_temp_file: bool = False,
) -> Dict[str, Any]:
    """
    执行 JavaScript 代码（使用 Node.js）

    Args:
        code: JavaScript 代码
        timeout: 超时时间（秒）
        keep_temp_file: 是否保留临时文件（用于调试）

    Returns:
        包含执行结果的字典：
        - success: 是否成功
        - output: 标准输出
        - error: 错误信息（如果有）
        - returncode: 返回码
        - temp_file: 临时文件路径（仅在 keep_temp_file=True 时）
    """
    # 获取项目根目录
    current_dir = Path(__file__).resolve().parent.parent.parent
    project_root = current_dir
    for parent in [current_dir] + list(current_dir.parents):
        if (parent / "package.json").exists():
            project_root = parent
            break

    # 创建临时文件
    temp_file = project_root / f"temp_exec_{id(code) & 0xFFFFFFFF}.js"

    try:
        temp_file.write_text(code, encoding='utf-8')

        # 设置环境变量
        env = {
            **os.environ,
            "NODE_PATH": str(project_root / "node_modules"),
        }

        # 执行 Node.js
        process = await asyncio.create_subprocess_exec(
            'node', str(temp_file),
            cwd=str(project_root),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )

        output = stdout.decode('utf-8', errors='replace').strip()
        error = stderr.decode('utf-8', errors='replace').strip()

        result = {
            'success': process.returncode == 0,
            'output': output,
            'error': error if error else None,
            'returncode': process.returncode,
        }

        # 如果请求保留临时文件，或执行失败，添加文件路径到结果中
        if keep_temp_file or not result['success']:
            result['temp_file'] = str(temp_file)

        # 如果执行成功且不保留临时文件，删除它
        if result['success'] and not keep_temp_file and temp_file.exists():
            temp_file.unlink()

        # 如果执行失败，在错误信息中添加文件位置提示
        if not result['success'] and temp_file.exists():
            error_hint = f"\n\n临时文件已保存至: {temp_file}"
            error_hint += f"\n可以手动运行调试: node {temp_file}"
            if result['error']:
                result['error'] = result['error'] + error_hint
            else:
                result['error'] = error_hint

        return result

    except asyncio.TimeoutError:
        # 超时时保留临时文件用于调试
        result = {
            'success': False,
            'error': f'代码执行超时（>{timeout}秒）',
            'returncode': -1,
        }
        if temp_file.exists():
            result['temp_file'] = str(temp_file)
            result['error'] += f"\n\n临时文件已保存至: {temp_file}"
            if not keep_temp_file:
                temp_file.unlink()
        return result
    except FileNotFoundError:
        return {
            'success': False,
            'error': 'Node.js 未安装，请先安装 Node.js',
            'returncode': -1,
        }
    except Exception as e:
        # 其他异常也保留临时文件用于调试
        result = {
            'success': False,
            'error': f'执行 JavaScript 代码时出错: {str(e)}',
            'returncode': -1,
        }
        if temp_file.exists():
            result['temp_file'] = str(temp_file)
            if not keep_temp_file:
                temp_file.unlink()
        return result


async def extract_and_execute_multi_language(
    agent_response: str,
    preferred_lang: Optional[str] = None,
    timeout: float = 30,
    keep_temp_file: bool = False,
) -> Dict[str, Any]:
    """
    从 Agent 响应中提取并执行代码（支持多语言）

    Args:
        agent_response: Agent 的响应文本
        preferred_lang: 首选语言（'python', 'javascript', 'bash'）
        timeout: 超时时间（秒）
        keep_temp_file: 是否保留临时文件（用于调试，仅对 JavaScript 有效）

    Returns:
        执行结果字典，包含 'language', 'code', 'success' 等字段
    """
    # 提取所有代码块
    codes = extract_code_from_text(agent_response)

    if not codes:
        return {
            'success': False,
            'error': '未找到可执行的代码块',
            'language': None,
            'code': None,
        }

    # 如果有首选语言，优先执行
    if preferred_lang and preferred_lang in codes:
        lang = preferred_lang
        code = codes[lang]
    else:
        # 按优先级选择：Python > JavaScript > Bash
        priority = ['python', 'javascript', 'bash']
        for lang in priority:
            if lang in codes:
                code = codes[lang]
                break
        else:
            # 如果都不匹配，选择第一个
            lang = list(codes.keys())[0]
            code = codes[lang]

    # 根据语言执行
    if lang == 'python':
        result = await execute_python_code_with_agentscope(code, timeout=timeout)
    elif lang == 'javascript':
        result = await execute_javascript_code(code, timeout=timeout, keep_temp_file=keep_temp_file)
    elif lang == 'bash':
        # TODO: 实现 Bash 执行
        result = {
            'success': False,
            'error': 'Bash 执行尚未实现',
        }
    else:
        result = {
            'success': False,
            'error': f'不支持的语言: {lang}',
        }

    # 添加语言和代码信息
    result['language'] = lang
    result['code'] = code

    return result
