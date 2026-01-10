"""
API Key 测试
测试 API Key 的加载和验证
"""

import sys
import io
from pathlib import Path

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_get_api_key():
    """测试获取 API Key"""
    from lingnexus.config import get_dashscope_api_key
    
    key = get_dashscope_api_key()
    assert key is not None, "API Key 未设置"
    assert len(key) > 0, "API Key 为空"
    print(f"✅ API Key 已加载: {key[:10]}...{key[-4:]}")
    return key


def test_require_api_key():
    """测试 require API Key（应该成功）"""
    from lingnexus.config import require_dashscope_api_key
    
    key = require_dashscope_api_key()
    assert key is not None
    print(f"✅ require_dashscope_api_key 成功: {key[:10]}...")
    return key


if __name__ == "__main__":
    print("=" * 60)
    print("API Key 测试")
    print("=" * 60)
    
    try:
        test_get_api_key()
        test_require_api_key()
        print("\n✅ 所有 API Key 测试通过")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

