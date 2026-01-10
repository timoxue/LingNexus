# 迁移到 Monorepo 架构

## 对现有用户的影响

### CLI 使用

**无变化**: 命令保持不变

```bash
# 旧方式（继续支持）
python -m lingnexus.cli monitor

# 新方式
uv run python -m lingnexus.cli monitor
```

### 代码导入

**兼容性**: 现有代码继续工作

```python
# 旧导入（继续支持）
from lingnexus.utils.skill_loader import SkillLoader

# 新导入（推荐）
from lingnexus.skill import SkillLoader
```

## 更新步骤

### 对于 Framework 用户

1. **更新依赖**: `pip install lingnexus-framework>=0.2.0`
2. **更新导入**: 使用新的导入路径（可选，旧路径仍支持）
3. **测试功能**: 运行现有测试确保兼容性

### 对于 Platform 用户

Platform 是新功能，需要单独部署。参考 [部署指南](docs/platform/deployment.md)。

### 对于开发者

1. **克隆仓库**: `git clone https://github.com/your-org/LingNexus`
2. **安装 uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. **同步依赖**: `uv sync`
4. **运行测试**: `bash scripts/test.sh`

## 目录结构变化

### 重构前

```
LingNexus/
├── lingnexus/           # 混合的代码
├── skills/
├── examples/
└── tests/
```

### 重构后

```
LingNexus/
├── packages/
│   ├── framework/       # 框架包（lingnexus-framework）
│   └── platform/        # 平台包（lingnexus-platform）
├── docs/
├── scripts/
└── [其他保持不变]
```

## 常见问题

### Q1: 导入错误

**问题**: `ModuleNotFoundError: No module named 'lingnexus'`

**解决**:
```bash
# 确保在工作区根目录
cd /path/to/LingNexus

# 重新同步依赖
uv sync

# 验证工作区配置
cat pyproject.toml | grep -A5 "\[tool.uv.workspace\]"
```

### Q2: 前端无法连接后端

**问题**: 前端显示 "Network Error"

**解决**:
```bash
# 检查 CORS 配置
# packages/platform/backend/main.py
# 确保 CORS_ORIGINS 包含前端地址

# 检查环境变量
cat packages/platform/backend/.env
```

### Q3: 测试失败

**问题**: pytest 找不到模块

**解决**:
```bash
# 设置 PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/packages/framework"

# 或使用 pytest.ini 配置
# [pytest]
# pythonpath = packages/framework
```

### Q4: 工作区不生效

**问题**: 修改 framework 后 platform 中没有更新

**解决**:
```bash
# 验证 uv 工作区配置
uv workspace verify

# 重新同步
uv sync --reinstall
```

## 版本历史

- **v0.2.0** (2025-01-10): Monorepo 架构重构
- **v0.1.9**: 重构前的最后一个单仓库版本

## 获取帮助

- 文档: [docs/](docs/)
- Issues: https://github.com/your-org/LingNexus/issues
- Discussions: https://github.com/your-org/LingNexus/discussions
- 邮箱: support@lingnexus.com
