#!/usr/bin/env python3
"""
自动生成的 Skill 注册代码
此文件由 load_claude_skills.py 自动生成
"""

from pathlib import Path

# 导入 AgentScope Toolkit
# AgentScope 的 Skill API 在 Toolkit 类中
try:
    from agentscope.tool import Toolkit
    AGENTSCOPE_AVAILABLE = True
except ImportError:
    print('⚠️  警告: 未安装 AgentScope')
    print('   提示: 使用 uv 安装: uv sync')
    print('   或使用 pip 安装: pip install agentscope')
    AGENTSCOPE_AVAILABLE = False
    Toolkit = None


def register_all_skills(toolkit: Toolkit | None = None):
    """注册所有发现的 Skills"""
    if not AGENTSCOPE_AVAILABLE:
        print('⚠️  警告: AgentScope 未安装，无法注册 Skills')
        return None
    
    if toolkit is None:
        toolkit = Toolkit()
    
    base_dir = Path(__file__).parent.parent
    
    # 注册所有 Skills
    skills_registered = 0
    skills_failed = 0
    
    # algorithmic-art (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/algorithmic-art')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 algorithmic-art 失败: {e}')
        skills_failed += 1

    # brand-guidelines (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/brand-guidelines')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 brand-guidelines 失败: {e}')
        skills_failed += 1

    # canvas-design (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/canvas-design')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 canvas-design 失败: {e}')
        skills_failed += 1

    # doc-coauthoring (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/doc-coauthoring')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 doc-coauthoring 失败: {e}')
        skills_failed += 1

    # docx (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/docx')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 docx 失败: {e}')
        skills_failed += 1

    # frontend-design (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/frontend-design')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 frontend-design 失败: {e}')
        skills_failed += 1

    # internal-comms (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/internal-comms')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 internal-comms 失败: {e}')
        skills_failed += 1

    # mcp-builder (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/mcp-builder')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 mcp-builder 失败: {e}')
        skills_failed += 1

    # pdf (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/pdf')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 pdf 失败: {e}')
        skills_failed += 1

    # pptx (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/pptx')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 pptx 失败: {e}')
        skills_failed += 1

    # skill-creator (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/skill-creator')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 skill-creator 失败: {e}')
        skills_failed += 1

    # slack-gif-creator (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/slack-gif-creator')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 slack-gif-creator 失败: {e}')
        skills_failed += 1

    # theme-factory (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/theme-factory')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 theme-factory 失败: {e}')
        skills_failed += 1

    # web-artifacts-builder (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/web-artifacts-builder')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 web-artifacts-builder 失败: {e}')
        skills_failed += 1

    # webapp-testing (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/webapp-testing')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 webapp-testing 失败: {e}')
        skills_failed += 1

    # xlsx (claude)
    try:
        toolkit.register_agent_skill(
            skill_dir=str(base_dir / 'skills/external/xlsx')
        )
        skills_registered += 1
    except Exception as e:
        print(f'❌ 注册 xlsx 失败: {e}')
        skills_failed += 1

    print(f'\n✅ 成功注册 {{skills_registered}} 个 Skills')
    if skills_failed > 0:
        print(f'⚠️  {{skills_failed}} 个 Skills 注册失败')
    
    return toolkit


if __name__ == '__main__':
    toolkit = register_all_skills()
    if toolkit:
        # 获取所有已注册技能的提示词
        prompt = toolkit.get_agent_skill_prompt()
        if prompt:
            print('\n📝 技能提示词已生成，可以附加到 Agent 的系统提示词中')
        print('✅ 所有 Skills 已注册')