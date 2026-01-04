"""
测试 Skill 优先级机制
验证 internal/ 目录的技能会覆盖 external/ 目录的同名技能
"""

from lingnexus.utils.skill_loader import SkillLoader


def test_skill_priority():
    """测试 internal 优先级"""
    print("=" * 60)
    print("测试 Skill 优先级机制")
    print("=" * 60)
    print()

    loader = SkillLoader()

    # 测试 1: docx 技能应该使用 internal 版本
    print("测试 1: docx 技能优先级")
    print("-" * 60)

    metadata = loader.load_skill_metadata_only("docx", skill_type="external")
    print(f"技能名称: {metadata['name']}")
    print(f"技能路径: {metadata['path']}")
    print(f"技能类型: {metadata['type']}")

    # 验证使用的是 internal 版本
    is_internal = "internal" in metadata['path']
    print(f"✅ 使用 internal 版本: {is_internal}")

    if is_internal:
        print("✅ 优先级机制正常工作")
    else:
        print("❌ 优先级机制未生效")

    print()

    # 测试 2: 检查 SKILL.md 内容
    print("测试 2: 检查 SKILL.md 内容")
    print("-" * 60)

    instructions = loader.load_skill_full_instructions("docx")
    has_line_break_warning = "CRITICAL: LINE BREAK RULES" in instructions
    print(f"✅ 包含换行规则警告: {has_line_break_warning}")

    if has_line_break_warning:
        print("✅ internal/docx/SKILL.md 的修改生效")
    else:
        print("❌ 使用的可能是 external 版本")

    print()

    # 测试 3: _resolve_skill_type 方法
    print("测试 3: 测试优先级解析方法")
    print("-" * 60)

    # docx 在 internal 存在，应该返回 internal
    resolved_type = loader._resolve_skill_type("docx", "external")
    print(f"_resolve_skill_type('docx', 'external') = {resolved_type}")
    print(f"✅ 返回 'internal': {resolved_type == 'internal'}")

    # 假设一个不存在的技能，应该返回 external
    fake_type = loader._resolve_skill_type("nonexistent_skill", "external")
    print(f"_resolve_skill_type('nonexistent_skill', 'external') = {fake_type}")
    print(f"✅ 返回 'external': {fake_type == 'external'}")

    print()

    # 测试 4: 完整路径验证
    print("测试 4: 验证文件存在性")
    print("-" * 60)

    from pathlib import Path
    internal_docx = Path("skills/internal/docx/SKILL.md")
    external_docx = Path("skills/external/docx/SKILL.md")

    print(f"internal/docx/SKILL.md 存在: {internal_docx.exists()}")
    print(f"external/docx/SKILL.md 存在: {external_docx.exists()}")

    if internal_docx.exists():
        print("✅ internal 版本存在")
    if external_docx.exists():
        print("✅ external 版本存在")

    print()

    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print()

    all_passed = (
        is_internal and
        has_line_break_warning and
        resolved_type == "internal" and
        fake_type == "external" and
        internal_docx.exists() and
        external_docx.exists()
    )

    if all_passed:
        print("✅ 所有测试通过！")
        print()
        print("优先级机制正常工作：")
        print("  1. ✅ internal/ 优先级高于 external/")
        print("  2. ✅ 自动检查并使用 internal 版本")
        print("  3. ✅ docx 技能的修改已生效")
        print("  4. ✅ 两个版本的文件都存在（可以对比）")
    else:
        print("⚠️ 部分测试未通过")
        if not is_internal:
            print("  ❌ 优先级机制未生效")
        if not has_line_break_warning:
            print("  ❌ internal 版本未使用")

    print()

    return all_passed


if __name__ == "__main__":
    test_skill_priority()
