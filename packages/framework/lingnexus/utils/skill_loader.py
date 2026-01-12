"""
Skill 加载器
用于加载和管理 Claude Skills
"""

import yaml
import re
import subprocess
import json
import sys
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

    def _resolve_skill_type(self, skill_name: str, skill_type: str = "external") -> str:
        """
        解析技能类型

        Args:
            skill_name: 技能名称
            skill_type: 技能类型（"external", "internal", 或 "auto"）
                        - "external": 强制使用 external 目录
                        - "internal": 强制使用 internal 目录
                        - "auto": 自动检测（优先 internal，其次 external）

        Returns:
            实际使用的技能类型（"internal" 或 "external"）
        """
        # 如果明确指定了类型，直接使用
        if skill_type in ["internal", "external"]:
            return skill_type

        # auto 模式：优先检查 internal 目录
        internal_path = self.skills_base_dir / "internal" / skill_name
        if internal_path.exists() and (internal_path / "SKILL.md").exists():
            return "internal"

        return "external"  # 默认使用 external
    
    def load_skill(self, skill_name: str, skill_type: str = "external") -> Dict:
        """
        加载单个技能的信息

        Args:
            skill_name: 技能名称（目录名）
            skill_type: 技能类型（"external", "internal"，默认 "external"）
                      注意：如果指定为 "external"，但 internal 目录存在同名技能，会优先使用 internal

        Returns:
            包含技能信息的字典
        """
        # 解析技能类型（internal 优先）
        skill_type = self._resolve_skill_type(skill_name, skill_type)
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

            # 1. 注册 SKILL.md 内容到 prompt
            self.toolkit.register_agent_skill(skill_dir=skill_info['path'])

            # 2. 尝试自动发现并注册 tools.py 中的工具函数
            tools_file = Path(skill_info['path']) / "scripts" / "tools.py"

            if tools_file.exists():
                try:
                    # 动态导入 tools 模块
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("skill_tools", tools_file)

                    if spec and spec.loader:
                        tools_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(tools_module)

                        # 查找所有工具函数（排除导入的类型和类）
                        import inspect
                        tool_functions = []
                        for attr_name in dir(tools_module):
                            attr = getattr(tools_module, attr_name)
                            # 检查是否是函数（不是类）
                            if inspect.isfunction(attr) and not attr_name.startswith('_'):
                                # 检查 __module__ 属性来排除内置函数和导入的函数
                                attr_module = getattr(attr, '__module__', None)
                                # 排除内置模块和标准库模块
                                if attr_module and not attr_module.startswith('_') and attr_module not in ['builtins', 'inspect', 'importlib', 'importlib.util', 'pathlib', 'typing', 'io', 'zipfile']:
                                    try:
                                        self.toolkit.register_tool_function(attr)
                                        tool_functions.append(attr_name)
                                    except Exception as e:
                                        import logging
                                        logging.warning(f"Failed to register tool {attr_name}: {e}")

                        if tool_functions:
                            import logging
                            logging.info(f"Skill '{skill_name}' registered {len(tool_functions)} tools: {tool_functions}")
                except Exception as e:
                    import logging
                    logging.warning(f"Failed to import tools from {tools_file}: {e}")

            return True
        except Exception as e:
            import logging
            logging.error(f"Failed to register skill '{skill_name}': {e}")
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
            skill_type: 技能类型（"external", "internal"，默认 "external"）
                      注意：如果指定为 "external"，但 internal 目录存在同名技能，会优先使用 internal

        Returns:
            只包含元数据的字典
        """
        # 解析技能类型（internal 优先）
        skill_type = self._resolve_skill_type(skill_name, skill_type)
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
            skill_type: 技能类型（"external", "internal"，默认 "external"）
                      注意：如果指定为 "external"，但 internal 目录存在同名技能，会优先使用 internal

        Returns:
            完整的 SKILL.md 内容
        """
        # 解析技能类型（internal 优先）
        skill_type = self._resolve_skill_type(skill_name, skill_type)
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
                      注意：如果指定为 "external"，但 internal 目录存在同名技能，会优先使用 internal

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
    
    def _tool_load_skill_reference(
        self, 
        skill_name: str, 
        reference_file: str, 
        skill_type: str = "external"
    ) -> ToolResponse:
        """
        工具函数：加载技能的参考文档（渐进式披露 - 阶段3：references 层）
        
        当 SKILL.md 中引用了参考文档时，使用此工具按需加载。
        参考文档可能位于：
        - references/ 目录（标准位置）
        - 技能根目录（旧格式，如 docx-js.md, ooxml.md）
        
        Args:
            skill_name: 技能名称（如 "docx", "pdf", "pptx"）
            reference_file: 参考文件名（如 "docx-js.md", "ooxml.md", "references/api_docs.md"）
            skill_type: 技能类型，默认为 "external"
        
        Returns:
            ToolResponse 对象，包含参考文档内容
        
        Example:
            load_skill_reference("docx", "docx-js.md")  # 加载 docx-js.md
            load_skill_reference("docx", "ooxml.md")    # 加载 ooxml.md
        """
        try:
            skill_path = self.skills_base_dir / skill_type / skill_name
            if not skill_path.exists():
                error_msg = f"❌ 错误: 找不到技能 {skill_name}"
                return ToolResponse(content=error_msg)
            
            # 尝试多个可能的路径
            possible_paths = [
                skill_path / reference_file,  # 根目录（旧格式）
                skill_path / "references" / reference_file,  # references/ 目录
                skill_path / reference_file.replace("references/", ""),  # 如果已经包含 references/
            ]
            
            reference_path = None
            for path in possible_paths:
                if path.exists() and path.is_file():
                    reference_path = path
                    break
            
            if reference_path is None:
                error_msg = f"❌ 错误: 找不到参考文档 {reference_file}（已尝试：根目录、references/ 目录）"
                return ToolResponse(content=error_msg)
            
            # 读取参考文档内容
            content_text = reference_path.read_text(encoding='utf-8')
            content = f"✅ 已加载 {skill_name} 技能的参考文档：{reference_file}\n\n{content_text}"
            return ToolResponse(content=content)
        
        except FileNotFoundError as e:
            error_msg = f"❌ 错误: 找不到参考文档 {reference_file} - {e}"
            return ToolResponse(content=error_msg)
        except Exception as e:
            error_msg = f"❌ 错误: 加载参考文档 {reference_file} 失败 - {e}"
            return ToolResponse(content=error_msg)
    
    def _tool_list_skill_resources(
        self, 
        skill_name: str, 
        skill_type: str = "external"
    ) -> ToolResponse:
        """
        工具函数：列出技能的所有资源（渐进式披露 - 阶段3：资源层）
        
        列出技能的 references/, assets/, scripts/ 目录中的文件。
        帮助 Agent 了解可用的资源。
        
        Args:
            skill_name: 技能名称（如 "docx", "pdf", "pptx"）
            skill_type: 技能类型，默认为 "external"
        
        Returns:
            ToolResponse 对象，包含资源列表
        """
        try:
            skill_path = self.skills_base_dir / skill_type / skill_name
            if not skill_path.exists():
                error_msg = f"❌ 错误: 找不到技能 {skill_name}"
                return ToolResponse(content=error_msg)
            
            result_lines = [f"📦 {skill_name} 技能的资源列表：\n"]
            
            # 检查 references/ 目录
            references_dir = skill_path / "references"
            if references_dir.exists() and references_dir.is_dir():
                ref_files = list(references_dir.glob("*"))
                if ref_files:
                    result_lines.append(f"\n📚 References/ 目录 ({len(ref_files)} 个文件):")
                    for f in sorted(ref_files)[:20]:  # 最多显示20个
                        if f.is_file():
                            size = f.stat().st_size
                            result_lines.append(f"   - {f.name} ({size} 字节)")
                    if len(ref_files) > 20:
                        result_lines.append(f"   ... 还有 {len(ref_files) - 20} 个文件")
            
            # 检查根目录的 .md 文件（旧格式的参考文档）
            root_md_files = list(skill_path.glob("*.md"))
            root_md_files = [f for f in root_md_files if f.name != "SKILL.md"]
            if root_md_files:
                result_lines.append(f"\n📄 根目录参考文档 ({len(root_md_files)} 个文件):")
                for f in sorted(root_md_files):
                    size = f.stat().st_size
                    result_lines.append(f"   - {f.name} ({size} 字节)")
            
            # 检查 assets/ 目录
            assets_dir = skill_path / "assets"
            if assets_dir.exists() and assets_dir.is_dir():
                asset_files = list(assets_dir.rglob("*"))
                asset_files = [f for f in asset_files if f.is_file()]
                if asset_files:
                    result_lines.append(f"\n🎨 Assets/ 目录 ({len(asset_files)} 个文件):")
                    for f in sorted(asset_files)[:20]:  # 最多显示20个
                        size = f.stat().st_size
                        rel_path = f.relative_to(assets_dir)
                        result_lines.append(f"   - {rel_path} ({size} 字节)")
                    if len(asset_files) > 20:
                        result_lines.append(f"   ... 还有 {len(asset_files) - 20} 个文件")
            
            # 检查 scripts/ 目录
            scripts_dir = skill_path / "scripts"
            if scripts_dir.exists() and scripts_dir.is_dir():
                script_files = list(scripts_dir.rglob("*"))
                script_files = [f for f in script_files if f.is_file() and f.suffix in ['.py', '.sh', '.js', '.ts']]
                if script_files:
                    result_lines.append(f"\n🔧 Scripts/ 目录 ({len(script_files)} 个文件):")
                    for f in sorted(script_files)[:20]:  # 最多显示20个
                        size = f.stat().st_size
                        rel_path = f.relative_to(scripts_dir)
                        result_lines.append(f"   - {rel_path} ({size} 字节)")
                    if len(script_files) > 20:
                        result_lines.append(f"   ... 还有 {len(script_files) - 20} 个文件")
            
            if len(result_lines) == 1:
                content = f"📭 {skill_name} 技能暂无资源文件"
                return ToolResponse(content=content)
            
            result_lines.append(
                "\n💡 提示: "
                "- 使用 `load_skill_reference(skill_name, reference_file)` 加载参考文档\n"
                "- 使用 `get_skill_resource_path(skill_name, resource_type)` 获取资源路径"
            )
            
            content = "\n".join(result_lines)
            return ToolResponse(content=content)
        
        except Exception as e:
            error_msg = f"❌ 错误: 列出资源失败 - {e}"
            return ToolResponse(content=error_msg)
    
    def _tool_get_skill_resource_path(
        self, 
        skill_name: str, 
        resource_type: str,  # "scripts", "assets", "references"
        skill_type: str = "external"
    ) -> ToolResponse:
        """
        工具函数：获取技能资源的路径（用于文件系统访问）
        
        返回资源的绝对路径，Agent 可以通过文件系统访问。
        适用于需要直接访问文件或执行脚本的场景。
        
        Args:
            skill_name: 技能名称（如 "docx", "pdf", "pptx"）
            resource_type: 资源类型（"scripts", "assets", "references"）
            skill_type: 技能类型，默认为 "external"
        
        Returns:
            ToolResponse 对象，包含资源路径
        
        Example:
            get_skill_resource_path("docx", "scripts")  # 获取 scripts 目录路径
        """
        try:
            skill_path = self.skills_base_dir / skill_type / skill_name
            if not skill_path.exists():
                error_msg = f"❌ 错误: 找不到技能 {skill_name}"
                return ToolResponse(content=error_msg)
            
            valid_types = ["scripts", "assets", "references"]
            if resource_type not in valid_types:
                error_msg = f"❌ 错误: 无效的资源类型 {resource_type}，有效类型：{', '.join(valid_types)}"
                return ToolResponse(content=error_msg)
            
            resource_path = skill_path / resource_type
            
            if not resource_path.exists():
                error_msg = f"❌ 错误: {skill_name} 技能没有 {resource_type}/ 目录"
                return ToolResponse(content=error_msg)
            
            # 返回绝对路径
            abs_path = resource_path.resolve()
            content = f"✅ {skill_name} 技能的 {resource_type}/ 目录路径：\n\n{abs_path}\n\n💡 提示: 可以通过此路径访问资源文件"
            return ToolResponse(content=content)
        
        except Exception as e:
            error_msg = f"❌ 错误: 获取资源路径失败 - {e}"
            return ToolResponse(content=error_msg)
    
    def _tool_check_and_fix_js(
        self,
        js_code: str,
    ) -> ToolResponse:
        """
        工具函数：检查和修复 JavaScript 代码（使用 js-checker skill）
        
        此工具会：
        1. 检查 Node.js 版本
        2. 修复全角符号等常见问题
        3. 检查代码语法
        4. 验证代码可执行性
        5. 返回执行命令供 execute_shell_command 使用
        
        Args:
            js_code: JavaScript 代码字符串
        
        Returns:
            ToolResponse 对象，包含检查结果和执行命令
        """
        try:
            # 查找 js-checker skill 的脚本路径
            js_checker_path = self.skills_base_dir / "internal" / "js-checker" / "scripts" / "check_and_fix_js.py"
            
            if not js_checker_path.exists():
                error_msg = "❌ 错误: js-checker skill 未找到"
                return ToolResponse(content=error_msg)
            
            # 调用检查脚本
            # 使用 errors='replace' 处理编码错误（Windows 系统可能输出 GBK 编码）
            process = subprocess.run(
                [sys.executable, str(js_checker_path), "-"],
                input=js_code,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # 处理编码错误，用替换字符代替无法解码的字节
                timeout=30,
            )
            
            if process.returncode != 0:
                error_msg = f"❌ 错误: 检查 JavaScript 代码失败\n{process.stderr}"
                return ToolResponse(content=error_msg)
            
            # 解析 JSON 结果
            try:
                check_result = json.loads(process.stdout)
            except json.JSONDecodeError as e:
                error_msg = f"❌ 错误: 解析检查结果失败 - {e}\n输出: {process.stdout}"
                return ToolResponse(content=error_msg)
            
            # 格式化返回结果
            result_lines = ["✅ JavaScript 代码检查完成\n"]
            
            # Node.js 版本信息
            node_version = check_result.get("node_version", {})
            if node_version.get("installed"):
                result_lines.append(f"📦 Node.js 版本: {node_version.get('version', 'unknown')}")
                if not node_version.get("meets_requirement"):
                    result_lines.append("⚠️  警告: Node.js 版本可能不支持某些语法特性")
            else:
                result_lines.append(f"❌ Node.js 未安装: {node_version.get('error', 'unknown')}")
            
            # 语法检查结果
            if check_result.get("syntax_ok"):
                result_lines.append("✅ 语法检查: 通过")
            else:
                result_lines.append("❌ 语法检查: 失败")
                if check_result.get("errors"):
                    result_lines.append(f"   错误: {check_result['errors'][0]}")
            
            # 修复信息
            fixes_applied = check_result.get("fixes_applied", [])
            if fixes_applied:
                result_lines.append(f"🔧 已修复 {len(fixes_applied)} 个问题:")
                for fix in fixes_applied[:5]:  # 最多显示5个
                    result_lines.append(f"   - {fix.get('type', 'unknown')}: {fix.get('original', '')} → {fix.get('fixed', '')}")
            
            # 验证结果
            if check_result.get("validation_ok"):
                result_lines.append("✅ 代码验证: 通过，可以执行")
            else:
                result_lines.append("⚠️  代码验证: 失败或未验证")
            
            # 执行命令
            execute_command = check_result.get("execute_command")
            if execute_command:
                result_lines.append(f"\n💡 执行命令（供 execute_shell_command 使用）:")
                result_lines.append(f"   {execute_command}")
            
            # 警告信息
            warnings = check_result.get("warnings", [])
            if warnings:
                result_lines.append(f"\n⚠️  警告:")
                for warning in warnings:
                    result_lines.append(f"   - {warning}")
            
            # 错误信息
            errors = check_result.get("errors", [])
            if errors:
                result_lines.append(f"\n❌ 错误:")
                for error in errors:
                    result_lines.append(f"   - {error}")
            
            content = "\n".join(result_lines)
            return ToolResponse(content=content)
        
        except subprocess.TimeoutExpired:
            error_msg = "❌ 错误: 检查 JavaScript 代码超时（>30秒）"
            return ToolResponse(content=error_msg)
        except Exception as e:
            error_msg = f"❌ 错误: 检查 JavaScript 代码失败 - {e}"
            return ToolResponse(content=error_msg)
    
    def get_progressive_tools(self) -> List:
        """
        获取渐进式披露工具函数列表
        
        这些工具函数可以注册到 Toolkit 供 Agent 使用。
        包括：
        - 阶段1：元数据层工具
        - 阶段2：指令层工具
        - 阶段3：资源层工具
        
        Returns:
            工具函数列表
        """
        return [
            self._tool_list_available_skills,      # 阶段1：列出可用技能（元数据）
            self._tool_load_skill_instructions,     # 阶段2：加载完整指令
            self._tool_load_skill_reference,       # 阶段3：加载参考文档
            self._tool_list_skill_resources,       # 阶段3：列出资源
            self._tool_get_skill_resource_path,     # 阶段3：获取资源路径
            self._tool_check_and_fix_js,           # 特殊工具：JavaScript 代码检查
        ]

