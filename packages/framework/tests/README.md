# 测试目录

包含所有测试脚本和测试用例。

## 测试文件

### 1. `test_setup.py` - 完整测试套件（推荐）

运行所有基础测试的完整套件：

```bash
uv run python tests/test_setup.py
```

**包含测试**：
- ✅ API Key 加载
- ✅ 模型创建（Qwen 和 DeepSeek）
- ✅ Skill 注册
- ✅ Agent 创建
- ⏭️  Agent 调用（可选，会消耗 API）

### 2. `test_api_key.py` - API Key 测试

测试 API Key 的加载和验证：

```bash
uv run python tests/test_api_key.py
```

### 3. `test_model_creation.py` - 模型创建测试

测试 Qwen 和 DeepSeek 模型的创建：

```bash
uv run python tests/test_model_creation.py
```

### 4. `test_skill_registration.py` - Skill 注册测试

测试 docx 技能的注册和加载：

```bash
uv run python tests/test_skill_registration.py
```

### 5. `test_agent_creation.py` - Agent 创建测试

测试 docx Agent 的创建：

```bash
uv run python tests/test_agent_creation.py
```

### 6. `test_cli.py` - CLI 交互式工具测试

全面的 CLI 功能测试，包括命令解析、模式切换、文件操作等：

```bash
uv run python tests/test_cli.py
```

**测试内容**：
- ✅ InteractiveTester 初始化
- ✅ 默认模型名称
- ✅ Agent 创建
- ✅ 命令解析（/help, /mode, /model, /execute, /history, /clear, /files, /exit 等）
- ✅ 响应提取
- ✅ Agent 调用（使用 mock）

### 8. `test_architecture.py` - 架构测试

验证 `interactive.py` 通过 `react_agent.py` 作为统一入口的架构：

```bash
uv run python tests/test_architecture.py
```

## 快速开始

### 运行所有测试

```bash
# 运行完整测试套件（推荐）
uv run python tests/test_setup.py
```

### 运行单个测试

```bash
# 测试 API Key
uv run python tests/test_api_key.py

# 测试模型创建
uv run python tests/test_model_creation.py

# 测试 Skill 注册
uv run python tests/test_skill_registration.py

# 测试 Agent 创建
uv run python tests/test_agent_creation.py

# 测试 CLI 功能
uv run python tests/test_cli.py

# 测试架构
uv run python tests/test_architecture.py
```

## 测试说明

### 基础测试（不消耗 API）

以下测试不会实际调用 API，只验证配置和初始化：
- ✅ API Key 加载
- ✅ 模型创建
- ✅ Skill 注册
- ✅ Agent 创建

### 功能测试（消耗 API）

以下测试会实际调用 API，消耗额度：
- ⚠️  Agent 调用测试（在 `test_setup.py` 中可选）

## 预期结果

如果所有测试通过，你应该看到：

```
✅ API Key 已加载: sk-xxxxx...xxxx
✅ Qwen 模型创建成功: qwen-max
✅ DeepSeek 模型创建成功: deepseek-chat
✅ docx 技能注册成功
✅ Agent 创建成功
```

## 故障排查

### API Key 未加载

**错误**：`❌ API Key 未加载`

**解决方法**：
1. 检查 `.env` 文件是否存在
2. 检查 `.env` 文件中是否包含 `DASHSCOPE_API_KEY=your_key`
3. 确保 `.env` 文件在项目根目录

### Skill 注册失败

**错误**：`❌ 技能注册失败`

**解决方法**：
1. 检查 `skills/external/docx` 目录是否存在
2. 检查 `skills/external/docx/SKILL.md` 文件是否存在
3. 确保 Skill 目录结构正确

### 模型创建失败

**错误**：`❌ 模型创建失败`

**解决方法**：
1. 检查 API Key 是否正确
2. 检查网络连接
3. 验证模型名称是否正确

## 更多信息

- 详细测试指南：`docs/testing_guide.md`
- API Key 管理：`docs/api_key_management.md`
- 使用示例：`examples/docx_agent_example.py`

