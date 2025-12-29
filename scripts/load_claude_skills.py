#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Skills 到 AgentScope 的加载器

此脚本用于将 Claude 格式的 Skills 加载到 AgentScope 中。
支持从 external/ 目录加载 Claude Skills，从 internal/ 目录加载自主开发的 Skills。

Usage:
    python scripts/load_claude_skills.py [--external-dir skills/external] [--internal-dir skills/internal]
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import yaml
import re
import io

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    import codecs
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def parse_skill_metadata(skill_path: Path) -> Optional[Dict]:
    """
    解析 Skill 的 SKILL.md 文件，提取元数据
    
    Args:
        skill_path: Skill 目录路径
        
    Returns:
        包含 name, description, license 等元数据的字典，如果解析失败返回 None
    """
    skill_md = skill_path / "SKILL.md"
    
    if not skill_md.exists():
        print(f"⚠️  警告: {skill_path} 中未找到 SKILL.md")
        return None
    
    try:
        content = skill_md.read_text(encoding='utf-8')
        
        # 提取 YAML front matter
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not yaml_match:
            print(f"⚠️  警告: {skill_path} 的 SKILL.md 中未找到 YAML front matter")
            return None
        
        yaml_content = yaml_match.group(1)
        metadata = yaml.safe_load(yaml_content)
        
        if not metadata:
            print(f"⚠️  警告: {skill_path} 的 YAML front matter 为空")
            return None
        
        # 验证必需字段
        if 'name' not in metadata:
            print(f"⚠️  警告: {skill_path} 缺少必需的 'name' 字段")
            return None
        
        if 'description' not in metadata:
            print(f"⚠️  警告: {skill_path} 缺少必需的 'description' 字段")
            return None
        
        # 添加路径信息
        metadata['path'] = str(skill_path)
        metadata['skill_type'] = 'claude' if 'external' in str(skill_path) else 'internal'
        
        return metadata
    
    except Exception as e:
        print(f"❌ 错误: 解析 {skill_path} 时出错: {e}")
        return None


def discover_skills(skills_dir: Path, skill_type: str = "unknown") -> List[Dict]:
    """
    发现指定目录下的所有 Skills
    
    Args:
        skills_dir: Skills 目录路径
        skill_type: Skill 类型 ('claude' 或 'internal')
        
    Returns:
        Skill 元数据列表
    """
    if not skills_dir.exists():
        print(f"⚠️  警告: 目录不存在: {skills_dir}")
        return []
    
    skills = []
    
    # 遍历目录，查找包含 SKILL.md 的子目录
    for item in skills_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            skill_md = item / "SKILL.md"
            if skill_md.exists():
                metadata = parse_skill_metadata(item)
                if metadata:
                    metadata['skill_type'] = skill_type
                    skills.append(metadata)
                    print(f"✅ 发现 {skill_type} skill: {metadata['name']} ({item.name})")
    
    return skills


def register_skill_to_agentscope(skill_metadata: Dict) -> bool:
    """
    将 Skill 注册到 AgentScope
    
    注意: 这需要根据 AgentScope 的实际 API 进行调整
    
    Args:
        skill_metadata: Skill 元数据
        
    Returns:
        是否注册成功
    """
    try:
        # 尝试导入 AgentScope Toolkit
        try:
            from agentscope.tool import Toolkit
        except ImportError:
            print("⚠️  警告: 未安装 AgentScope，跳过注册")
            print(f"   提示: 使用 uv 安装: uv sync")
            print(f"   或使用 pip 安装: pip install agentscope")
            return False
        
        # 注册 Skill
        skill_path = Path(skill_metadata['path'])
        toolkit = Toolkit()
        toolkit.register_agent_skill(
            skill_dir=str(skill_path)
        )
        
        print(f"✅ 已注册: {skill_metadata['name']}")
        return True
    
    except Exception as e:
        print(f"❌ 注册 {skill_metadata['name']} 时出错: {e}")
        return False


def generate_skill_registry(skills: List[Dict], output_file: Optional[Path] = None) -> str:
    """
    生成 Skill 注册代码
    
    Args:
        skills: Skill 元数据列表
        output_file: 输出文件路径（可选）
        
    Returns:
        生成的 Python 代码字符串
    """
    code_lines = [
        "#!/usr/bin/env python3",
        '"""',
        "自动生成的 Skill 注册代码",
        "此文件由 load_claude_skills.py 自动生成",
        '"""',
        "",
        "from pathlib import Path",
        "",
        "# 导入 AgentScope Toolkit",
        "# AgentScope 的 Skill API 在 Toolkit 类中",
        "try:",
        "    from agentscope.tool import Toolkit",
        "    AGENTSCOPE_AVAILABLE = True",
        "except ImportError:",
        "    print('⚠️  警告: 未安装 AgentScope')",
        "    print('   提示: 使用 uv 安装: uv sync')",
        "    print('   或使用 pip 安装: pip install agentscope')",
        "    AGENTSCOPE_AVAILABLE = False",
        "    Toolkit = None",
        "",
        "",
        "def register_all_skills(toolkit: Toolkit | None = None):",
        "    \"\"\"注册所有发现的 Skills\"\"\"",
        "    if not AGENTSCOPE_AVAILABLE:",
        "        print('⚠️  警告: AgentScope 未安装，无法注册 Skills')",
        "        return None",
        "    ",
        "    if toolkit is None:",
        "        toolkit = Toolkit()",
        "    ",
        "    base_dir = Path(__file__).parent.parent",
        "    ",
        "    # 注册所有 Skills",
        "    skills_registered = 0",
        "    skills_failed = 0",
        "    ",
    ]
    
    for skill in skills:
        skill_path = Path(skill['path'])
        # 计算相对路径，处理绝对路径和相对路径
        try:
            if skill_path.is_absolute():
                relative_path = skill_path.relative_to(Path.cwd())
            else:
                relative_path = skill_path
        except ValueError:
            # 如果无法计算相对路径，使用绝对路径
            relative_path = skill_path
        
        # 转换为使用正斜杠的字符串（跨平台兼容）
        path_str = str(relative_path).replace('\\', '/')
        code_lines.append(f"    # {skill['name']} ({skill.get('skill_type', 'unknown')})")
        code_lines.append(f"    try:")
        code_lines.append(f"        toolkit.register_agent_skill(")
        code_lines.append(f"            skill_dir=str(base_dir / '{path_str}')")
        code_lines.append(f"        )")
        code_lines.append(f"        skills_registered += 1")
        code_lines.append(f"    except Exception as e:")
        code_lines.append(f"        print(f'❌ 注册 {skill['name']} 失败: {{e}}')")
        code_lines.append(f"        skills_failed += 1")
        code_lines.append("")
    
    code_lines.extend([
        "    print(f'\\n✅ 成功注册 {{skills_registered}} 个 Skills')",
        "    if skills_failed > 0:",
        "        print(f'⚠️  {{skills_failed}} 个 Skills 注册失败')",
        "    ",
        "    return toolkit",
        "",
        "",
        "if __name__ == '__main__':",
        "    toolkit = register_all_skills()",
        "    if toolkit:",
        "        # 获取所有已注册技能的提示词",
        "        prompt = toolkit.get_agent_skill_prompt()",
        "        if prompt:",
        "            print('\\n📝 技能提示词已生成，可以附加到 Agent 的系统提示词中')",
        "        print('✅ 所有 Skills 已注册')",
    ])
    
    code = "\n".join(code_lines)
    
    if output_file:
        output_file.write_text(code, encoding='utf-8')
        print(f"✅ 已生成注册代码: {output_file}")
    
    return code


def main():
    parser = argparse.ArgumentParser(
        description="加载 Claude Skills 到 AgentScope",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 加载所有 Skills
  python scripts/load_claude_skills.py
  
  # 指定目录
  python scripts/load_claude_skills.py --external-dir skills/external --internal-dir skills/internal
  
  # 仅生成注册代码，不实际注册
  python scripts/load_claude_skills.py --generate-only
        """
    )
    
    parser.add_argument(
        '--external-dir',
        type=Path,
        default=Path('skills/external'),
        help='Claude Skills 目录 (默认: skills/external)'
    )
    
    parser.add_argument(
        '--internal-dir',
        type=Path,
        default=Path('skills/internal'),
        help='自主开发 Skills 目录 (默认: skills/internal)'
    )
    
    parser.add_argument(
        '--generate-only',
        action='store_true',
        help='仅生成注册代码，不实际注册到 AgentScope'
    )
    
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('scripts/register_skills.py'),
        help='注册代码输出文件 (默认: scripts/register_skills.py)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Claude Skills 到 AgentScope 加载器")
    print("=" * 60)
    print()
    
    # 发现 Skills
    print("🔍 正在发现 Skills...")
    print()
    
    external_skills = discover_skills(args.external_dir, "claude")
    internal_skills = discover_skills(args.internal_dir, "internal")
    
    all_skills = external_skills + internal_skills
    
    print()
    print(f"📊 统计: 发现 {len(external_skills)} 个 Claude Skills, {len(internal_skills)} 个内部 Skills")
    print(f"   总计: {len(all_skills)} 个 Skills")
    print()
    
    if not all_skills:
        print("⚠️  未发现任何 Skills")
        return
    
    # 生成注册代码
    print("📝 正在生成注册代码...")
    generate_skill_registry(all_skills, args.output)
    print()
    
    # 如果不需要实际注册，则退出
    if args.generate_only:
        print("✅ 仅生成模式，未实际注册")
        return
    
    # 尝试注册到 AgentScope
    print("🚀 正在注册到 AgentScope...")
    print()
    
    registered_count = 0
    for skill in all_skills:
        if register_skill_to_agentscope(skill):
            registered_count += 1
    
    print()
    print("=" * 60)
    print(f"✅ 完成: 成功注册 {registered_count}/{len(all_skills)} 个 Skills")
    print("=" * 60)
    print()
    print("💡 提示: 可以使用生成的 scripts/register_skills.py 来注册所有 Skills")


if __name__ == '__main__':
    main()

