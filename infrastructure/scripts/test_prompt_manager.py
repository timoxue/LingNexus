#!/usr/bin/env python3
"""
Prompt 管理系统测试脚本

运行方式：
    python test_prompt_manager.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.prompts.manager import prompt_manager


def test_load_prompts():
    """测试 Prompt 配置加载"""
    print("=" * 60)
    print("测试 1: Prompt 配置加载")
    print("=" * 60)
    
    # 列出情报服务的所有 Prompt
    intel_prompts = prompt_manager.list_prompts("intelligence")
    print(f"\n情报服务共有 {len(intel_prompts)} 个 Prompt：")
    for p in intel_prompts:
        print(f"  - {p['key']}: {p['description']}")
        print(f"    推荐模型: {p['recommended_model']}, 版本: {p['version']}")
    
    # 列出 BD 服务的 Prompt
    bd_prompts = prompt_manager.list_prompts("bd")
    print(f"\nBD 服务共有 {len(bd_prompts)} 个 Prompt：")
    for p in bd_prompts:
        print(f"  - {p['key']}: {p['description']}")
    
    # 列出 RD 服务的 Prompt
    rd_prompts = prompt_manager.list_prompts("rd")
    print(f"\nRD 服务共有 {len(rd_prompts)} 个 Prompt：")
    for p in rd_prompts:
        print(f"  - {p['key']}: {p['description']}")
    
    print("\n✅ Prompt 配置加载成功！\n")


def test_render_prompt():
    """测试 Prompt 渲染"""
    print("=" * 60)
    print("测试 2: Prompt 渲染")
    print("=" * 60)
    
    # 渲染情报分析 Prompt
    query = "阿司匹林在中国的临床试验进展"
    context = "关注近三年的 III 期临床数据"
    
    rendered = prompt_manager.render(
        service="intelligence",
        key="intelligence_summary_v1",
        query=query,
        context=context,
    )
    
    print(f"\n原始变量：")
    print(f"  query: {query}")
    print(f"  context: {context}")
    
    print(f"\n渲染后的 Prompt（前 300 字符）：")
    print("-" * 60)
    print(rendered[:300] + "...")
    print("-" * 60)
    
    print("\n✅ Prompt 渲染成功！\n")


def test_get_metadata():
    """测试获取 Prompt 元数据"""
    print("=" * 60)
    print("测试 3: 获取 Prompt 元数据")
    print("=" * 60)
    
    metadata = prompt_manager.get_metadata(
        service="intelligence",
        key="intelligence_summary_detailed_v1"
    )
    
    print(f"\nPrompt 元数据：")
    print(f"  描述: {metadata['description']}")
    print(f"  版本: {metadata['version']}")
    print(f"  推荐模型: {metadata['recommended_model']}")
    print(f"  语言: {metadata['locale']}")
    
    # 测试获取推荐模型
    model = prompt_manager.get_recommended_model("intelligence", "intelligence_quick_extract_v1")
    print(f"\n快速提取 Prompt 推荐模型: {model}")
    
    print("\n✅ 元数据获取成功！\n")


def test_error_handling():
    """测试错误处理"""
    print("=" * 60)
    print("测试 4: 错误处理")
    print("=" * 60)
    
    # 测试不存在的服务
    try:
        prompt_manager.render("nonexistent_service", "some_key", query="test")
        print("❌ 应该抛出 KeyError")
    except KeyError as e:
        print(f"✅ 正确捕获错误: {e}")
    
    # 测试不存在的 key
    try:
        prompt_manager.render("intelligence", "nonexistent_key", query="test")
        print("❌ 应该抛出 KeyError")
    except KeyError as e:
        print(f"✅ 正确捕获错误: {e}")
    
    # 测试缺少必需变量
    try:
        prompt_manager.render("intelligence", "intelligence_summary_v1", query="test")
        # 缺少 context 参数
        print("❌ 应该抛出 KeyError")
    except KeyError as e:
        print(f"✅ 正确捕获错误: {e}")
    
    print("\n✅ 错误处理正常！\n")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Prompt 管理系统测试")
    print("=" * 60 + "\n")
    
    try:
        test_load_prompts()
        test_render_prompt()
        test_get_metadata()
        test_error_handling()
        
        print("=" * 60)
        print("所有测试通过！ 🎉")
        print("=" * 60)
        print("\n提示：")
        print("  - 已加载的 Prompt 配置文件：")
        print("    - shared/prompts/intelligence.yaml")
        print("    - shared/prompts/bd.yaml")
        print("    - shared/prompts/rd.yaml")
        print("\n  - 你可以在 workflow 中使用：")
        print("    from shared.prompts.manager import prompt_manager")
        print("    prompt_text = prompt_manager.render(...)")
        print()
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
