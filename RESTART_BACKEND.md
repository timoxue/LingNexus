# 重启 Backend 服务以加载 API Key

## 步骤 1: 停止当前 Backend 服务

在运行 Backend 的终端窗口按 `Ctrl+C` 停止服务。

## 步骤 2: 重新启动 Backend

```bash
cd D:\LingNexus\packages\platform\backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 步骤 3: 验证环境变量已加载

Backend 启动后，应该在日志中看到：
```
Loaded environment variables from D:\LingNexus\.env
```

## 步骤 4: 测试 Agent 执行

1. 访问 http://localhost:5173/agents
2. 点击 "docx助手"
3. 输入消息："创建一个空文件erp.docx"
4. 点击执行

## 问题排查

如果仍然报错 "No api key provided"，请检查：

### 1. 确认 .env 文件存在
```bash
cat D:\LingNexus\.env
```

应该看到：
```
DASHSCOPE_API_KEY=sk-57056cdaa1ec49c883e585d7ce1ea3d5
```

### 2. 手动设置环境变量（临时方案）

如果重启后仍有问题，可以手动设置环境变量：

**Windows PowerShell**:
```powershell
$env:DASHSCOPE_API_KEY="sk-57056cdaa1ec49c883e585d7ce1ea3d5"
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Windows CMD**:
```cmd
set DASHSCOPE_API_KEY=sk-57056cdaa1ec49c883e585d7ce1ea3d5
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 检查 API Key 是否有效

访问 https://dashscope.console.aliyun.com/ 确认 API key 是否有效且未过期。

## 修改内容

### main.py
添加了环境变量加载逻辑：
- 从项目根目录加载 `.env` 文件
- 如果找不到 .env 文件，输出警告日志
- 如果 python-dotenv 未安装，输出警告日志

### pyproject.toml
添加了依赖：
- `python-dotenv>=1.0.0`

## 为什么需要重启？

Python 进程在启动时读取环境变量，运行时无法动态加载新的环境变量。因此需要重启 Backend 进程来加载新配置的 API key。
