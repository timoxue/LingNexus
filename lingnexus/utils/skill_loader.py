"""
Skill 加载器
用于加载和管理 Claude Skills
"""

import yaml
import re
from pathlib import Path
from typing import Dict, Optional, List
from agentscope.tool import Toolkit


class SkillLoader:
    """加载和管理 Skills"""
    
    def __init__(self, skills_base_dir: str | Path = "skills"):
        """
        初始化 Skill 加载器
        
        Args:
            skills_base_dir: Skills 基础目录路径
        """
        self.skills_base_dir = Path(skills_base_dir)
        self.toolkit = Toolkit()
        self._loaded_skills: Dict[str, Dict] = {}
    
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

