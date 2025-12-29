# API Key 管理指南

## 概述

DeepSeek 和 Qwen 都使用 DashScope API，需要设置 `DASHSCOPE_API_KEY`。

## 快速设置

### 方式 1: 环境变量（推荐，生产环境）

```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your_api_key"

# Linux/Mac
export DASHSCOPE_API_KEY="your_api_key"

# 永久设置（Linux/Mac）
echo 'export DASHSCOPE_API_KEY="your_api_key"' >> ~/.bashrc
source ~/.bashrc
```

### 方式 2: .env 文件（推荐，开发环境）

1. 复制示例文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件：
```
DASHSCOPE_API_KEY=your_api_key
```

3. 代码会自动读取 `.env` 文件

### 方式 3: 代码中传入（不推荐）

```python
from lingnexus.agent import create_docx_agent
from lingnexus.config import ModelType

agent = create_docx_agent(
    model_type=ModelType.QWEN,
    api_key="your_api_key",  # 直接传入
)
```

## 获取 API Key

### Qwen（通义千问）

1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 注册/登录账号
3. 创建 API Key
4. 复制 API Key

### DeepSeek

1. 访问 [DeepSeek 官网](https://www.deepseek.com/)
2. 注册/登录账号
3. 进入 API 管理页面
4. 创建 API Key
5. 复制 API Key

## 优先级顺序

API Key 的读取优先级：

1. **函数参数**（最高优先级）
2. **环境变量** `DASHSCOPE_API_KEY`
3. **.env 文件** `DASHSCOPE_API_KEY`
4. **None**（如果都未设置）

## 验证设置

```python
from lingnexus.config import get_dashscope_api_key, require_dashscope_api_key

# 检查是否设置了 API Key
key = get_dashscope_api_key()
if key:
    print(f"✅ API Key 已设置: {key[:10]}...{key[-4:]}")
else:
    print("❌ API Key 未设置")

# 获取 API Key（如果未设置会抛出异常）
try:
    key = require_dashscope_api_key()
    print(f"✅ API Key: {key[:10]}...{key[-4:]}")
except ValueError as e:
    print(f"❌ {e}")
```

## 安全建议

1. **不要提交 API Key 到版本控制**
   - `.env` 文件已在 `.gitignore` 中
   - 不要将 API Key 硬编码到代码中

2. **使用环境变量（生产环境）**
   - 更安全
   - 便于管理

3. **定期轮换 API Key**
   - 提高安全性
   - 防止泄露

4. **限制 API Key 权限**
   - 只授予必要的权限
   - 定期检查使用情况

## 故障排查

### 问题：API Key 未设置

**错误信息**：`ValueError: DashScope API Key 未设置`

**解决方法**：
1. 检查 `.env` 文件是否存在
2. 检查 `.env` 文件中是否包含 `DASHSCOPE_API_KEY=your_key`
3. 检查环境变量是否设置
4. 确保 `.env` 文件在项目根目录

### 问题：API Key 无效

**错误信息**：API 调用失败

**解决方法**：
1. 检查 API Key 是否正确复制（没有多余空格）
2. 检查 API Key 是否过期
3. 检查账户余额是否充足
4. 验证 API Key 是否有效

## 相关文件

- `lingnexus/config/api_keys.py` - API Key 管理模块
- `.env.example` - 示例配置文件
- `docs/testing.md` - 测试指南（包含 API Key 测试）

