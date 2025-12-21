# Skill → Plugin → Plugin Store 架构设计

## 1. 架构概览

LingNexus 采用三层插件化架构，实现从底层能力到用户应用的完整生态：

```
┌─────────────────────────────────────────────────────────────┐
│                    Plugin Store (用户层)                     │
│  - Web UI: React + Vite + TypeScript                       │
│  - Backend BFF: FastAPI (端口 8020)                         │
│  - 功能: 插件浏览、安装、运行                                │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP API
┌─────────────────────────────────────────────────────────────┐
│                 Plugin Runtime (执行层)                      │
│  - 服务: FastAPI (端口 8015)                                │
│  - 功能: 插件加载、沙箱执行、生命周期管理                     │
│  - 自动发现: 扫描 plugins/ 目录                              │
└─────────────────────────────────────────────────────────────┘
                            ↓ get_skill()
┌─────────────────────────────────────────────────────────────┐
│                    Skills (能力层)                           │
│  - 注册机制: @register_skill 装饰器                          │
│  - 存储: shared/skills/ 按领域组织                           │
│  - 复用: 被 Plugins 调用执行业务逻辑                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 核心概念

### 2.1 Skill (技能)

**定位**: 底层原子能力，面向**开发者/Agent**

**特征**:
- ✅ 细粒度、单一职责
- ✅ 通过 `@register_skill` 注册到全局 Registry
- ✅ 可被 Agent、Workflow、Plugin 调用
- ✅ 不直接面向终端用户

**示例**:
```python
# shared/skills/intelligence/fetch_news.py
@register_skill
class FetchNewsSkill(BaseSkill):
    name: str = "intel.fetch_news"
    description: str = "根据主题与关键词检索医药资讯"
    domain: str = "intelligence"
    
    async def execute(self, input_data: FetchNewsInput) -> SkillOutput:
        # 底层业务逻辑
        return SkillOutput(success=True, data=news_items)
```

**注册后调用**:
```python
from shared.skills.registry import get_skill

skill = get_skill("intel.fetch_news")
result = await skill.execute(input_data)
```

---

### 2.2 Plugin (插件)

**定位**: 业务场景包装，面向**终端用户**

**特征**:
- ✅ 组合一个或多个 Skill
- ✅ 提供用户友好的输入/输出
- ✅ 通过 `plugin_manifest.json` 定义元信息
- ✅ 自动生成前端表单（基于 input_schema）
- ✅ 支持权限控制、版本管理

**目录结构**:
```
plugins/
├── news_quick_search/              # 插件目录
│   ├── plugin_manifest.json        # 元信息（必需）
│   ├── main.py                     # 入口函数（必需）
│   └── __init__.py                 # Python 包标识
└── intel_daily_digest/
    ├── plugin_manifest.json
    ├── main.py
    └── __init__.py
```

**plugin_manifest.json 示例**:
```json
{
  "plugin_id": "com.lingnexus.intel.news-quick-search",
  "version": "1.0.0",
  "name": "新闻快速搜索",
  "description": "根据关键词快速检索医药新闻资讯",
  "category": "intelligence",
  "tags": ["搜索", "新闻", "资讯"],
  
  "required_skills": ["intel.fetch_news"],
  "entrypoint": "plugins.news_quick_search.main:run_plugin",
  
  "input_schema": {
    "type": "object",
    "properties": {
      "topic_name": {
        "type": "string",
        "description": "搜索主题名称"
      },
      "keywords": {
        "type": "array",
        "items": {"type": "string"}
      }
    },
    "required": ["topic_name"]
  },
  
  "permissions": ["read_pharma_news"]
}
```

**main.py 入口函数**:
```python
from shared.skills.plugin import plugin_entrypoint
from shared.skills.registry import get_skill

@plugin_entrypoint
async def run_plugin(payload: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
    # 1. 提取用户输入
    topic_name = payload.get("topic_name")
    keywords = payload.get("keywords", [])
    
    # 2. 获取底层 Skill（关键！）
    fetch_news_skill = get_skill("intel.fetch_news")
    
    # 3. 调用 Skill 执行
    skill_output = await fetch_news_skill.execute(FetchNewsInput(
        topic_name=topic_name,
        keywords=keywords
    ))
    
    # 4. 返回用户友好格式
    return {
        "status": "success",
        "news_count": len(skill_output.data),
        "news_items": skill_output.data
    }
```

---

### 2.3 Plugin Store (插件商店)

**定位**: 用户应用入口，提供**可视化管理界面**

**技术栈**:
- **前端**: React + Vite + TypeScript (端口 5173)
- **后端 BFF**: FastAPI (端口 8020)
- **数据源**: Plugin Runtime API

**核心功能**:

1. **插件浏览**
   - 展示所有已安装插件
   - 显示插件信息（名称、描述、版本、标签）
   - 启用/禁用状态管理

2. **插件详情**
   - 查看完整的 input_schema 和 output_schema
   - 自动生成输入表单（基于 JSON Schema）
   - 展示插件权限和依赖

3. **插件运行**
   - 用户填写表单参数
   - 调用 Plugin Runtime API 执行
   - 实时显示执行结果

**数据流向**:
```
用户在浏览器填写表单
    ↓
Plugin Store Frontend (5173)
    ↓ /api/plugins/{id}/run
Plugin Store Backend (8020)
    ↓ HTTP 请求
Plugin Runtime (8015)
    ↓ 加载并执行
plugins/ 目录中的插件
    ↓ get_skill()
调用底层 Skill
    ↓
返回结果 → 用户
```

---

## 3. Skill 到 Plugin 转换流程

### 步骤 1: 确认 Skill 已注册

```bash
# 检查 Skill 是否可用
from shared.skills.registry import get_skill
skill = get_skill("intel.fetch_news")
print(skill.name, skill.description)
```

### 步骤 2: 创建插件目录

```bash
mkdir -p plugins/news_quick_search
cd plugins/news_quick_search
```

### 步骤 3: 编写 plugin_manifest.json

定义插件的所有元信息：
- 基本信息（ID、名称、版本）
- 依赖的 Skill (`required_skills`)
- 输入/输出 Schema（符合 JSON Schema 标准）
- 权限声明
- 入口函数路径

**关键点**: `input_schema` 必须符合 JSON Schema 标准格式：
```json
{
  "type": "object",
  "properties": {
    "field_name": {
      "type": "string",
      "description": "字段说明"
    }
  },
  "required": ["field_name"]
}
```

### 步骤 4: 编写 main.py 入口函数

```python
from shared.skills.plugin import plugin_entrypoint
from shared.skills.registry import get_skill
from shared.skills.intelligence.fetch_news import FetchNewsInput

@plugin_entrypoint
async def run_plugin(payload: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
    # 核心逻辑：通过 get_skill() 调用底层能力
    skill = get_skill("intel.fetch_news")
    skill_output = await skill.execute(FetchNewsInput(...))
    return {"status": "success", "data": skill_output.data}
```

### 步骤 5: 创建 __init__.py

```bash
touch __init__.py
```

### 步骤 6: 重启 Plugin Runtime

```bash
# Plugin Runtime 启动时会自动扫描 plugins/ 目录
python -m uvicorn plugin_runtime.server:app --port 8015
```

### 步骤 7: 验证插件已上架

访问 Plugin Store 前端或调用 API：
```bash
curl http://localhost:8015/store/plugins
```

---

## 4. 关键设计原则

### 4.1 单一数据源原则

**Plugin Runtime 是唯一的数据和执行源**，Plugin Store 只是展示层：

- ✅ Plugin Store Backend 不存储插件数据
- ✅ 所有数据通过 HTTP 从 Plugin Runtime 获取
- ✅ 插件执行完全由 Plugin Runtime 负责

### 4.2 插件复用 Skill 原则

**插件不重复实现业务逻辑**：

- ✅ 插件通过 `get_skill()` 获取已注册的 Skill
- ✅ 插件只负责参数转换和结果格式化
- ✅ 底层逻辑变更时，插件无需修改

**反例**（❌ 不推荐）:
```python
async def run_plugin(payload):
    # ❌ 直接实现业务逻辑，而不是调用 Skill
    news = await fetch_from_database(...)
    return news
```

**正例**（✅ 推荐）:
```python
async def run_plugin(payload):
    # ✅ 调用已有的 Skill
    skill = get_skill("intel.fetch_news")
    result = await skill.execute(...)
    return result.data
```

### 4.3 自动发现原则

**Plugin Runtime 启动时自动发现插件**：

- ✅ 扫描 `plugins/` 目录下的所有 `plugin_manifest.json`
- ✅ 验证 manifest 合法性
- ✅ 注册到插件管理器
- ✅ 无需手动配置

**实现**:
```python
# plugin_runtime/plugin_loader.py
def discover_manifests() -> List[PluginManifest]:
    plugins_dir = Path(__file__).parent.parent / "plugins"
    manifests = []
    for manifest_path in plugins_dir.rglob("plugin_manifest.json"):
        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = PluginManifest(**json.load(f))
            manifests.append(manifest)
    return manifests
```

### 4.4 前端表单自动生成原则

**基于 input_schema 自动生成输入表单**：

- ✅ `type: "string"` → 文本输入框
- ✅ `type: "number"` → 数字输入框
- ✅ `type: "array"` → 多行文本框
- ✅ `type: "string", enum: [...]` → 下拉选择框
- ✅ `required: [...]` → 必填标识（*）

**前端实现**:
```typescript
// plugin_store/frontend/src/pages/PluginDetail.tsx
const renderInputField = (key: string, schema: any) => {
  if (schema.type === 'string' && schema.enum) {
    return <select>...</select>;
  }
  if (schema.type === 'array') {
    return <textarea placeholder="每行一个值">...</textarea>;
  }
  return <input type="text" />;
};
```

---

## 5. 目录结构

```
LingNexus/
├── shared/
│   └── skills/                    # Skill 层
│       ├── intelligence/          # 情报领域
│       │   ├── fetch_news.py     # 新闻检索 Skill
│       │   └── generate_daily_digest.py
│       ├── registry.py            # Skill 注册表
│       └── plugin.py              # 插件开发工具
│
├── plugins/                       # Plugin 层（安装位置）
│   ├── news_quick_search/
│   │   ├── plugin_manifest.json
│   │   ├── main.py
│   │   └── __init__.py
│   └── intel_daily_digest/
│       ├── plugin_manifest.json
│       ├── main.py
│       └── __init__.py
│
├── plugin_runtime/                # Plugin Runtime 层
│   ├── server.py                 # FastAPI 服务 (8015)
│   ├── manager.py                # 插件管理器
│   ├── plugin_loader.py          # 自动发现
│   └── models.py                 # 数据模型
│
└── plugin_store/                  # Plugin Store 层
    ├── backend/                   # BFF 层 (8020)
    │   └── api.py
    └── frontend/                  # Web UI (5173)
        ├── src/
        │   ├── pages/
        │   │   ├── PluginList.tsx
        │   │   └── PluginDetail.tsx
        │   └── api/
        │       └── plugins.ts
        └── vite.config.ts
```

---

## 6. 服务启动顺序

```bash
# 1️⃣ 启动 Plugin Runtime (必需)
conda activate lingnexus
python -m uvicorn plugin_runtime.server:app --host 0.0.0.0 --port 8015

# 2️⃣ 启动 Plugin Store Backend (必需)
python -m uvicorn plugin_store.backend.api:app --host 0.0.0.0 --port 8020

# 3️⃣ 启动 Plugin Store Frontend (开发模式)
cd plugin_store/frontend
npm run dev
```

访问: http://localhost:5173

---

## 7. API 端点

### Plugin Runtime (8015)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/store/plugins` | GET | 获取所有插件列表 |
| `/plugins/{id}/detail` | GET | 获取插件详情 |
| `/plugins/{id}/invoke` | POST | 执行插件 |
| `/store/plugins/{id}/enable` | POST | 启用插件 |
| `/store/plugins/{id}/disable` | POST | 禁用插件 |

### Plugin Store Backend (8020)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/plugins` | GET | 透传 Runtime 插件列表 |
| `/api/plugins/{id}` | GET | 透传 Runtime 插件详情 |
| `/api/plugins/{id}/run` | POST | 透传 Runtime 执行请求 |

---

## 8. 数据模型

### PluginManifest
```python
class PluginManifest(BaseModel):
    plugin_id: str
    version: str
    name: str
    description: str
    author: str
    category: str
    tags: List[str]
    required_skills: List[str]
    entrypoint: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    permissions: List[str]
```

### PluginStoreItem (列表展示)
```python
class PluginStoreItem(BaseModel):
    plugin_id: str
    name: str
    version: str
    description: str
    tags: List[str]
    enabled: bool
```

### PluginDetail (详情页)
```python
class PluginDetail(PluginStoreItem):
    author: str
    required_skills: List[str]
    permissions: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
```

---

## 9. 插件开发最佳实践

### ✅ DO (推荐)

1. **使用 @plugin_entrypoint 装饰器**
   ```python
   @plugin_entrypoint
   async def run_plugin(payload, context):
       ...
   ```

2. **通过 get_skill() 调用底层能力**
   ```python
   skill = get_skill("domain.skill_name")
   result = await skill.execute(input_data)
   ```

3. **input_schema 符合 JSON Schema 标准**
   ```json
   {
     "type": "object",
     "properties": {...},
     "required": [...]
   }
   ```

4. **提供清晰的错误信息**
   ```python
   if not topic_name:
       return {"status": "error", "error": "缺少必需参数：topic_name"}
   ```

### ❌ DON'T (不推荐)

1. ❌ 在插件中重复实现业务逻辑
2. ❌ input_schema 缺少 `type: "object"` 包装
3. ❌ 硬编码配置，应使用环境变量或配置文件
4. ❌ 忽略异常处理

---

## 10. 扩展性设计

### 10.1 支持远程插件仓库

**未来可扩展**：
- 从远程仓库下载插件
- 插件版本升级管理
- 插件依赖解析

### 10.2 支持插件市场

**未来可扩展**：
- 插件评分和评论
- 插件使用统计
- 插件推荐算法

### 10.3 支持多租户

**未来可扩展**：
- 用户级插件管理
- 插件权限控制
- 插件配额限制

---

## 11. 常见问题

### Q1: 如何调试插件？

**方法 1**: 查看 Plugin Runtime 日志
```bash
# 日志会显示插件执行过程
tail -f logs/plugin_runtime.log
```

**方法 2**: 在 main.py 中添加日志
```python
from shared.utils.logging_utils import get_logger
logger = get_logger(__name__)

logger.info("插件参数", extra={"payload": payload})
```

### Q2: 为什么插件返回结果为空？

**检查清单**：
1. ✅ Skill 是否正确注册？使用 `get_skill()` 验证
2. ✅ 输入参数格式是否正确？检查日志
3. ✅ 底层数据是否存在？检查 `data/pharma_news.json`
4. ✅ 搜索关键词是否匹配？尝试不同关键词

### Q3: 前端显示"插件已禁用"？

**原因**: `PluginDetail` 模型缺少 `enabled` 字段

**解决**: 确保后端返回数据包含 `enabled: true`

### Q4: 前端没有显示输入表单？

**原因**: `input_schema` 格式不符合 JSON Schema 标准

**解决**: 确保 schema 有 `type: "object"` 和 `properties` 包装层

---

## 12. 版本历史

- **v0.1** (2025-12-20): 初始架构设计
  - 实现 Skill 注册机制
  - 实现 Plugin Runtime 基础功能
  - 实现 Plugin Store Web UI
  - 完成 2 个示例插件（intel_daily_digest, news_quick_search）
