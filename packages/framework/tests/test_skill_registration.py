"""
Skill 注册测试
测试 docx 技能的注册和加载
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


def test_register_docx_skill():
    """测试注册 docx 技能"""
    from lingnexus.utils import SkillLoader
    
    loader = SkillLoader()
    success = loader.register_skill("docx", skill_type="external")
    assert success, "docx 技能注册失败"
    print("✅ docx 技能注册成功")
    return loader


def test_get_skill_prompt():
    """测试获取技能提示词"""
    from lingnexus.utils import SkillLoader
    
    loader = SkillLoader()
    loader.register_skill("docx", skill_type="external")
    prompt = loader.get_skill_prompt()
    assert prompt is not None, "技能提示词为空"
    assert len(prompt) > 0, "技能提示词为空字符串"
    print(f"✅ 技能提示词获取成功（长度: {len(prompt)} 字符）")
    print(f"   预览: {prompt[:100]}...")
    return prompt


def test_get_skill_scripts_path():
    """测试获取技能脚本路径"""
    from lingnexus.utils import SkillLoader
    
    loader = SkillLoader()
    scripts_path = loader.get_skill_scripts_path("docx")
    if scripts_path:
        print(f"✅ docx 技能脚本路径: {scripts_path}")
        assert scripts_path.exists(), "脚本路径不存在"
    else:
        print("⚠️  docx 技能没有 scripts 目录（这是正常的）")
    return scripts_path


if __name__ == "__main__":
    print("=" * 60)
    print("Skill 注册测试")
    print("=" * 60)
    
    try:
        test_register_docx_skill()
        test_get_skill_prompt()
        test_get_skill_scripts_path()
        print("\n✅ 所有 Skill 注册测试通过")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

