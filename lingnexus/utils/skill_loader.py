"""
Skill 加载器
用于加载和管理 Claude Skills
"""

import yaml
import re
from pathlib import Path
from typing import Dict, Optional, List
from agentscope.tool import Toolkit, ToolResponse


class SkillLoader:
    """加载和管理 Skills，支持渐进式披露"""
    
    def __init__(self, skills_base_dir: str | Path = "skills"):
        """
        初始化 Skill 加载器
        
        Args:
            skills_base_dir: Skills 基础目录路径
        """
        self.skills_base_dir = Path(skills_base_dir)
        self.toolkit = Toolkit()
        self._loaded_skills: Dict[str, Dict] = {}
        self._metadata_cache: Dict[str, Dict] = {}  # 元数据缓存
        self._full_instructions_cache: Dict[str, str] = {}  # 完整指令缓存
    
    def load_skill(self, skill_name: str, skill_type: str = "external") -> Dict:
        """
        加载单个技能的信息
        
        Args:
            skill_name: 技能名称（目录名）
            skill_type: 技能类型（"external" 或 "internal"）
        
        Returns:
            包含技能信息的字典
        """
        skill_path = self.skills_base_dir / skill_type / skill_name
        
        if not skill_path.exists():
            raise FileNotFoundError(f"Skill 目录不存在: {skill_path}")
        
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            raise FileNotFoundError(f"Skill 文件不存在: {skill_md}")
        
        # 解析 SKILL.md
        content = skill_md.read_text(encoding='utf-8')
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        
        if not yaml_match:
            raise ValueError(f"Skill {skill_name} 的 SKILL.md 中未找到 YAML front matter")
        
        yaml_content = yaml_match.group(1)
        metadata = yaml.safe_load(yaml_content)
        
        if not metadata or 'name' not in metadata:
            raise ValueError(f"Skill {skill_name} 缺少必需的元数据")
        
        skill_info = {
            'name': metadata['name'],
            'description': metadata.get('description', ''),
            'path': str(skill_path),
            'type': skill_type,
            'metadata': metadata,
        }
        
        self._loaded_skills[skill_name] = skill_info
        return skill_info
    
    def register_skill(self, skill_name: str, skill_type: str = "external") -> bool:
        """
        注册技能到 Toolkit
        
        Args:
            skill_name: 技能名称
            skill_type: 技能类型
        
        Returns:
            是否注册成功
        """
        try:
            skill_info = self.load_skill(skill_name, skill_type)
            self.toolkit.register_agent_skill(skill_dir=skill_info['path'])
            return True
        except Exception as e:
            print(f"❌ 注册技能 {skill_name} 失败: {e}")
            return False
    
    def register_skills(self, skill_names: List[str], skill_type: str = "external") -> int:
        """
        批量注册技能
        
        Args:
            skill_names: 技能名称列表
            skill_type: 技能类型
        
        Returns:
            成功注册的技能数量
        """
        success_count = 0
        for skill_name in skill_names:
            if self.register_skill(skill_name, skill_type):
                success_count += 1
        return success_count
    
    def get_skill_scripts_path(self, skill_name: str) -> Optional[Path]:
        """
        获取技能的 scripts 目录路径
        
        Args:
            skill_name: 技能名称
        
        Returns:
            scripts 目录路径，如果不存在则返回 None
        """
        if skill_name not in self._loaded_skills:
            return None
        
        skill_path = Path(self._loaded_skills[skill_name]['path'])
        scripts_path = skill_path / "scripts"
        
        return scripts_path if scripts_path.exists() else None
    
    def get_skill_prompt(self) -> Optional[str]:
        """
        获取所有已注册技能的提示词
        
        Returns:
            技能提示词字符串，如果没有注册任何技能则返回 None
        """
        return self.toolkit.get_agent_skill_prompt()
    
    def get_toolkit(self) -> Toolkit:
        """
        获取 Toolkit 实例
        
        Returns:
            Toolkit 实例
        """
        return self.toolkit
    
    def load_skill_metadata_only(self, skill_name: str, skill_type: str = "external") -> Dict:
        """
        只加载技能的元数据（阶段1：渐进式披露）
        
        Args:
            skill_name: 技能名称
            skill_type: 技能类型
        
        Returns:
            只包含元数据的字典
        """
        cache_key = f"{skill_type}:{skill_name}"
        if cache_key in self._metadata_cache:
            return self._metadata_cache[cache_key]
        
        skill_path = self.skills_base_dir / skill_type / skill_name
        if not skill_path.exists():
            raise FileNotFoundError(f"Skill 目录不存在: {skill_path}")
        
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            raise FileNotFoundError(f"Skill 文件不存在: {skill_md}")
        
        # 只读取前几行，提取 YAML front matter
        content = skill_md.read_text(encoding='utf-8')
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        
        if not yaml_match:
            raise ValueError(f"Skill {skill_name} 的 SKILL.md 中未找到 YAML front matter")
        
        yaml_content = yaml_match.group(1)
        metadata = yaml.safe_load(yaml_content)
        
        if not metadata or 'name' not in metadata:
            raise ValueError(f"Skill {skill_name} 缺少必需的元数据")
        
        metadata_info = {
            'name': metadata['name'],
            'description': metadata.get('description', ''),
            'path': str(skill_path),
            'type': skill_type,
        }
        
        self._metadata_cache[cache_key] = metadata_info
        return metadata_info
    
    def load_all_skills_metadata(self, skill_type: str = "external") -> List[Dict]:
        """
        扫描并加载所有 Skills 的元数据（阶段1）
        
        Args:
            skill_type: 技能类型
        
        Returns:
            元数据列表
        """
        skills_dir = self.skills_base_dir / skill_type
        if not skills_dir.exists():
            return []
        
        metadata_list = []
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                try:
                    metadata = self.load_skill_metadata_only(skill_dir.name, skill_type)
                    metadata_list.append(metadata)
                except Exception as e:
                    print(f"⚠️ 加载 {skill_dir.name} 元数据失败: {e}")
        
        return metadata_list
    
    def load_skill_full_instructions(self, skill_name: str, skill_type: str = "external") -> str:
        """
        加载技能的完整指令（阶段2：渐进式披露）
        
        Args:
            skill_name: 技能名称
            skill_type: 技能类型
        
        Returns:
            完整的 SKILL.md 内容
        """
        cache_key = f"{skill_type}:{skill_name}"
        if cache_key in self._full_instructions_cache:
            return self._full_instructions_cache[cache_key]
        
        skill_path = self.skills_base_dir / skill_type / skill_name
        skill_md = skill_path / "SKILL.md"
        
        if not skill_md.exists():
            raise FileNotFoundError(f"Skill 文件不存在: {skill_md}")
        
        # 读取完整的 SKILL.md
        full_content = skill_md.read_text(encoding='utf-8')
        
        self._full_instructions_cache[cache_key] = full_content
        return full_content
    
    def get_skills_metadata_prompt(self, skill_type: str = "external") -> str:
        """
        生成只包含元数据的提示词（阶段1）
        
        Args:
            skill_type: 技能类型
        
        Returns:
            元数据提示词
        """
        metadata_list = self.load_all_skills_metadata(skill_type)
        
        if not metadata_list:
            return ""
        
        prompt_lines = [
            "## 可用技能列表（元数据）",
            "",
            "以下是可用的技能，每个技能只显示名称和描述。",
            "当你需要某个技能时，请使用 `load_skill_instructions` 工具加载该技能的完整指令。",
            "",
        ]
        
        for metadata in metadata_list:
            prompt_lines.append(f"### {metadata['name']}")
            prompt_lines.append(f"**描述**: {metadata['description']}")
            prompt_lines.append("")
        
        prompt_lines.append(
            "**注意**: 不要直接使用这些技能。"
            "当你确定需要使用某个技能时，先调用 `load_skill_instructions` 工具加载完整指令。"
        )
        
        return "\n".join(prompt_lines)
    
    def _tool_load_skill_instructions(self, skill_name: str, skill_type: str = "external") -> ToolResponse:
        """
        工具函数：加载指定技能的完整指令（渐进式披露 - 阶段2）
        
        当你确定需要使用某个技能时，调用此工具来加载该技能的完整指令。
        完整指令包含详细的使用方法、工作流程和示例。
        
        Args:
            skill_name: 技能名称（如 "docx", "pdf", "pptx"）
            skill_type: 技能类型，默认为 "external"（外部技能）
        
        Returns:
            ToolResponse 对象，包含技能的完整指令内容
        
        Example:
            load_skill_instructions("docx")  # 加载 docx 技能的完整指令
        """
        try:
            instructions = self.load_skill_full_instructions(skill_name, skill_type)
            
            # 同时注册到 Toolkit（如果需要访问资源）
            try:
                skill_info = self.load_skill_metadata_only(skill_name, skill_type)
                self.toolkit.register_agent_skill(skill_dir=skill_info['path'])
            except Exception as e:
                # 注册失败不影响返回指令
                pass
            
            content = f"✅ 已加载 {skill_name} 技能的完整指令：\n\n{instructions}"
            return ToolResponse(content=content)
        
        except FileNotFoundError as e:
            error_msg = f"❌ 错误: 找不到技能 {skill_name} - {e}"
            return ToolResponse(content=error_msg)
        except Exception as e:
            error_msg = f"❌ 错误: 加载技能 {skill_name} 失败 - {e}"
            return ToolResponse(content=error_msg)
    
    def _tool_list_available_skills(self, skill_type: str = "external") -> ToolResponse:
        """
        工具函数：列出所有可用技能的元数据（渐进式披露 - 阶段1）
        
        Args:
            skill_type: 技能类型，默认为 "external"
        
        Returns:
            ToolResponse 对象，包含所有可用技能的元数据列表
        """
        try:
            metadata_list = self.load_all_skills_metadata(skill_type)
            
            if not metadata_list:
                content = f"📭 未找到 {skill_type} 类型的技能"
                return ToolResponse(content=content)
            
            result_lines = [f"📋 可用技能列表 ({len(metadata_list)} 个):\n"]
            
            for i, metadata in enumerate(metadata_list, 1):
                result_lines.append(
                    f"{i}. **{metadata['name']}**\n"
                    f"   描述: {metadata['description']}\n"
                )
            
            result_lines.append(
                "\n💡 提示: 使用 `load_skill_instructions(skill_name)` 加载某个技能的完整指令"
            )
            
            content = "\n".join(result_lines)
            return ToolResponse(content=content)
        
        except Exception as e:
            error_msg = f"❌ 错误: 列出技能失败 - {e}"
            return ToolResponse(content=error_msg)
    
    def get_progressive_tools(self) -> List:
        """
        获取渐进式披露工具函数列表
        
        这些工具函数可以注册到 Toolkit 供 Agent 使用。
        
        Returns:
            工具函数列表
        """
        return [
            self._tool_load_skill_instructions,
            self._tool_list_available_skills,
        ]

