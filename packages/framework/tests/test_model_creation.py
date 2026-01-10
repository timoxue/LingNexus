"""
模型创建测试
测试 Qwen 和 DeepSeek 模型的创建
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


def test_create_qwen_model():
    """测试创建 Qwen 模型"""
    from lingnexus.config import create_model, ModelType
    
    model = create_model(ModelType.QWEN, model_name="qwen-max")
    assert model is not None
    assert model.model_name == "qwen-max"
    print(f"✅ Qwen 模型创建成功: {model.model_name}")
    return model


def test_create_deepseek_model():
    """测试创建 DeepSeek 模型"""
    from lingnexus.config import create_model, ModelType
    
    model = create_model(ModelType.DEEPSEEK, model_name="deepseek-chat")
    assert model is not None
    assert model.model_name == "deepseek-chat"
    print(f"✅ DeepSeek 模型创建成功: {model.model_name}")
    return model


def test_get_formatter():
    """测试获取 Formatter"""
    from lingnexus.config import get_formatter, ModelType
    
    formatter = get_formatter(ModelType.QWEN)
    assert formatter is not None
    print(f"✅ Formatter 获取成功: {type(formatter).__name__}")
    return formatter


if __name__ == "__main__":
    print("=" * 60)
    print("模型创建测试")
    print("=" * 60)
    
    try:
        test_create_qwen_model()
        test_create_deepseek_model()
        test_get_formatter()
        print("\n✅ 所有模型创建测试通过")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

