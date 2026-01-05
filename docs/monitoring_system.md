# 竞品情报监控系统

**版本**: v1.0
**更新日期**: 2026-01-05
**状态**: ✅ 生产就绪

## 目录

- [系统概述](#系统概述)
- [架构设计](#架构设计)
- [数据存储](#数据存储)
- [数据源配置](#数据源配置)
- [使用指南](#使用指南)
- [开发指南](#开发指南)

---

## 系统概述

竞品情报监控系统是LingNexus的核心功能模块，用于自动化采集、存储和分析医药领域的竞争情报数据。

### 核心功能

- ✅ **自动化监控**: 定时采集临床试验、申报进度等数据
- ✅ **多数据源支持**: ClinicalTrials.gov、CDE、Insight等
- ✅ **三层存储**: 原始数据、向量数据库、结构化数据库
- ✅ **智能分析**: 语义搜索、变化检测、竞品对比
- ✅ **CLI工具**: 统一的命令行管理接口

### 监控的项目

系统当前监控项目：

**司美格鲁肽** (Semaglutide) - 糖尿病GLP-1受体激动剂 ⭐

**详细信息**:
- **商品名**: Ozempic（注射剂）、Rybelsus（口服片）、Wegovy（减重）
- **关注适应症**:
  - 糖尿病（已上市）
  - 减重（已上市）
  - 心血管（研究中）
  - NASH（研究中）
  - 阿尔茨海默病（研究中）
- **竞争企业**: 诺和诺德、华东医药、丽珠集团、联邦制药

---

## 架构设计

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     LingNexus CLI                           │
│  python -m lingnexus.cli (统一入口)                         │
└──────────────┬──────────────────────────────────────────────┘
               │
               ├─► chat          → 交互式Agent对话
               ├─► monitor      → 执行监控任务
               ├─► status       → 查看监控状态
               ├─► db           → 查询数据库
               ├─► search       → 语义搜索
               └─► report       → 生成报告（待实现）

┌──────────────────────────────────────────────────────────────┐
│                   监控调度器                                 │
│  lingnexus/scheduler/monitoring.py                         │
│  - 配置文件加载                                              │
│  - 项目遍历                                                  │
│  - 数据源优先级管理                                          │
│  - 数据采集协调                                              │
└──────────────┬───────────────────────────────────────────────┘
               │
               ├─► ClinicalTrials.gov爬虫 (API v2)
               ├─► CDE爬虫 (Playwright自动化)
               └─► Insight爬虫 (待实现)

┌──────────────────────────────────────────────────────────────┐
│                   三层存储架构                               │
├──────────────────────────────────────────────────────────────┤
│  1. 原始数据存储 (lingnexus/storage/raw.py)                 │
│     - 保存完整HTML/JSON                                     │
│     - 按日期和项目组织                                       │
│     - 位置: data/raw/                                       │
│                                                              │
│  2. 向量数据库 (lingnexus/storage/vector.py)               │
│     - ChromaDB (可选)                                       │
│     - 语义搜索能力                                          │
│     - 位置: data/vectordb/                                  │
│                                                              │
│  3. 结构化数据库 (lingnexus/storage/structured.py)         │
│     - SQLAlchemy ORM + SQLite                               │
│     - 项目管理、临床试验、申报进度                           │
│     - 位置: data/intelligence.db                            │
└──────────────────────────────────────────────────────────────┘
```

### 模块组织

```
lingnexus/
├── cli/                        # 统一CLI入口
│   ├── __main__.py            # 主入口（子命令路由）
│   ├── interactive.py         # 交互式对话
│   └── monitoring.py          # 监控命令
│
├── scheduler/                  # 调度器
│   └── monitoring.py          # 每日监控任务
│
└── storage/                    # 存储层
    ├── raw.py                 # 原始数据存储
    ├── vector.py              # 向量数据库（可选）
    └── structured.py          # 结构化数据库

skills/internal/intelligence/   # Intelligence Skill
└── scripts/
    ├── clinical_trials_scraper.py  # ClinicalTrials.gov爬虫
    └── cde_scraper.py              # CDE爬虫

config/
└── projects_monitoring.yaml   # 项目配置文件
```

---

## 数据存储

### 1. 原始数据存储

**目的**: 保存完整的原始数据，确保可追溯性

**位置**: `data/raw/{source}/{date}/`

**文件命名**: `{source}_{YYYYMMDD}_{HHMMSS}_{hash}.json`

**使用方法**:
```python
from lingnexus.storage.raw import RawStorage

storage = RawStorage()

# 保存数据
data_id = storage.save(
    source="ClinicalTrials.gov",
    data='{"full": "json data"}',
    url="https://...",
    project="司美格鲁肽"
)

# 加载数据
data, metadata = storage.load(data_id)

# 列出项目的所有数据
files = storage.list_by_project("司美格鲁肽")
```

### 2. 向量数据库

**目的**: 提供语义搜索能力（可选）

**技术**: ChromaDB

**位置**: `data/vectordb/`

**使用方法**:
```python
from lingnexus.storage.vector import VectorDB

vectordb = VectorDB()

# 添加文档
vectordb.add(
    data_id="unique_id",
    text="临床试验的完整文本...",
    metadata={
        "source": "ClinicalTrials.gov",
        "project": "司美格鲁肽",
        "collected_at": "2026-01-05"
    }
)

# 搜索
results = vectordb.search(
    query="司美格鲁肽肥胖症",
    n_results=5,
    filter={"project": "司美格鲁肽"}
)
```

**注意**: ChromaDB在Windows上需要C++编译器。如果未安装，系统会自动跳过向量存储功能。

### 3. 结构化数据库

**目的**: 提供高效查询和统计分析

**技术**: SQLAlchemy ORM + SQLite

**位置**: `data/intelligence.db`

**数据模型**:

```python
# 项目表
Project
├── id (Integer)
├── name (String) - 项目名称
├── english_name (String) - 英文名称
├── category (String) - 分类
└── clinical_trials (Relationship)

# 临床试验表
ClinicalTrial
├── id (Integer)
├── nct_id (String) - NCT编号
├── title (String) - 标题
├── company (String) - 公司名称
├── phase (String) - 阶段
├── status (String) - 状态
├── indication (String) - 适应症
├── start_date (Date) - 开始日期
├── completion_date (Date) - 完成日期
├── enrollment (Integer) - 入组人数
├── source (String) - 来源
├── url (String) - URL
├── raw_data_id (String) - 原始数据ID
├── project_id (Integer) - 项目ID
└── collected_at (DateTime) - 采集时间
```

**使用方法**:
```python
from lingnexus.storage.structured import StructuredDB

db = StructuredDB()

# 保存试验数据
db.save_trial(
    raw_data_id="ct_20260105_...",
    extracted_data={
        "nct_id": "NCT06989203",
        "title": "Protein Supplementation...",
        "company": "Test Pharma",
        "phase": "PHASE2",
        "status": "RECRUITING",
        # ...
    },
    project_name="司美格鲁肽"
)

# 查询项目的试验
trials = db.get_project_trials("司美格鲁肽", limit=50)

# 查询所有项目
projects = db.get_all_projects()

db.close()
```

---

## 数据源配置

### 配置文件

**位置**: `config/projects_monitoring.yaml`

**结构**:
```yaml
monitored_projects:
  - name: "司美格鲁肽"
    english_name: "Semaglutide"
    category: "糖尿病"
    keywords:
      - "semaglutide"
      - "GLP-1"
    data_sources:
      - source: "ClinicalTrials.gov"
        priority: 1
      - source: "CDE"
        priority: 1
      - source: "Insight"
        priority: 1

  - name: "帕利哌酮微晶"
    category: "精神分裂症"
    keywords:
      - "paliperidone"
      - "帕利哌酮"
    data_sources:
      - source: "ClinicalTrials.gov"
        priority: 1
      - source: "CDE"
        priority: 2
```

### 支持的数据源

| 数据源 | 状态 | 优先级 | 实现方式 |
|--------|------|--------|----------|
| **ClinicalTrials.gov** | ✅ 完成 | 1 | API v2 |
| **CDE** | ⚠️ 框架完成 | 1 | Playwright |
| **Insight** | ⏳ 待实现 | 1 | 需要手动登录 |
| **WHO-ICTRP** | ⏳ 待实现 | 3 | 待设计 |
| **FDA** | ⏳ 待实现 | 2 | 待设计 |

### ClinicalTrials.gov爬虫

**文件**: `skills/internal/intelligence/scripts/clinical_trials_scraper.py`

**API端点**: `https://clinicaltrials.gov/api/v2/studies`

**功能**:
- ✅ 搜索临床试验（多关键词）
- ✅ 获取研究详情
- ✅ 完整的JSON解析
- ✅ 数据验证和清洗

**使用示例**:
```python
from skills.internal.intelligence.scripts.clinical_trials_scraper import ClinicalTrialsGovScraper

scraper = ClinicalTrialsGovScraper()

# 搜索试验
trials = scraper.search_trials(
    keyword="semaglutide",
    max_results=10
)

for trial in trials:
    print(f"{trial['nct_id']}: {trial['title']}")
```

### CDE爬虫

**文件**: `skills/internal/intelligence/scripts/cde_scraper.py`

**技术**: Playwright浏览器自动化

**功能**:
- ✅ 智能选择器匹配
- ✅ 正则表达式提取
- ✅ 上下文管理器（自动关闭浏览器）
- ✅ 延迟控制（避免被封）
- ⚠️ **需要现场调整页面选择器**

**当前状态**: 框架完成，需要实际访问CDE网站调整选择器

---

## 使用指南

### CLI命令速查

```bash
# ========================================
# 交互式对话（默认）
# ========================================
python -m lingnexus.cli
python -m lingnexus.cli chat --model qwen --mode test

# ========================================
# 监控管理
# ========================================
# 监控所有项目
python -m lingnexus.cli monitor

# 监控单个项目
python -m lingnexus.cli monitor --project "司美格鲁肽"

# 查看监控状态
python -m lingnexus.cli status

# ========================================
# 数据库查询
# ========================================
# 查看所有数据
python -m lingnexus.cli db

# 查看特定项目
python -m lingnexus.cli db --project "司美格鲁肽"

# 查看特定试验
python -m lingnexus.cli db --nct NCT06989203

# ========================================
# 语义搜索（需要ChromaDB）
# ========================================
python -m lingnexus.cli search "司美格鲁肽肥胖症"
python -m lingnexus.cli search "关键词" --project "司美格鲁肽" --n 10
```

### Python API

#### 1. 执行监控

```python
from lingnexus.scheduler.monitoring import DailyMonitoringTask

task = DailyMonitoringTask()

# 监控所有项目
results = task.run()

# 监控特定项目
results = task.run(project_names=["司美格鲁肽"])

# 查看结果
for project, data in results.items():
    if "error" in data:
        print(f"❌ {project}: {data['error']}")
    else:
        total = sum(len(r.get('items', [])) for r in data.values())
        print(f"✅ {project}: {total} 条数据")
```

#### 2. 查询数据库

```python
from lingnexus.storage.structured import StructuredDB

db = StructuredDB()

# 获取所有项目
projects = db.get_all_projects()
for project in projects:
    print(f"{project['name']} - {project.get('english_name', 'N/A')}")

# 获取项目的试验
trials = db.get_project_trials("司美格鲁肽", limit=20)
for trial in trials:
    print(f"{trial['nct_id']}: {trial['title']}")
    print(f"  状态: {trial['status']}, 阶段: {trial['phase']}")

# 查询特定试验
from lingnexus.storage.structured import ClinicalTrial
trial = db.session.query(ClinicalTrial).filter_by(
    nct_id="NCT06989203"
).first()

if trial:
    print(f"标题: {trial.title}")
    print(f"公司: {trial.company}")
    print(f"状态: {trial.status}")

db.close()
```

#### 3. 使用原始数据

```python
from lingnexus.storage.raw import RawStorage

storage = RawStorage()

# 列出项目的所有原始数据
files = storage.list_by_project("司美格鲁肽")
print(f"找到 {len(files)} 个原始文件")

for file_info in files[:5]:
    print(f"{file_info['data_id']}: {file_info['url']}")

# 加载特定原始数据
if files:
    data, metadata = storage.load(files[0]['data_id'])
    print(f"原始数据: {data[:200]}...")
    print(f"元数据: {metadata}")
```

---

## 开发指南

### 添加新的数据源

1. **创建爬虫脚本**
   ```bash
   # 在 skills/internal/intelligence/scripts/ 下创建
   touch new_source_scraper.py
   ```

2. **实现爬虫类**
   ```python
   class NewSourceScraper:
       def search_trials(self, keyword: str, max_results: int = 10):
           # 实现搜索逻辑
           pass
   ```

3. **在monitoring.py中注册**
   ```python
   # lingnexus/scheduler/monitoring.py
   def _scrape_new_source(self, project: Dict) -> Dict:
       from skills.internal.intelligence.scripts.new_source_scraper import NewSourceScraper

       scraper = NewSourceScraper()
       trials = scraper.search_trials(keyword)
       # ...
   ```

4. **更新配置文件**
   ```yaml
   data_sources:
     - source: "NewSource"
       priority: 1
   ```

### 数据类型处理

**重要**: SQLite的Date类型只接受Python date对象，不接受字符串。

系统已自动处理日期转换（`_clean_dates`方法），支持的格式：
- `YYYY-MM-DD` (如: "2026-01-05")
- `YYYY-MM` (如: "2026-01")
- `YYYY` (如: "2026")

### 可选依赖处理

**ChromaDB是可选的**。如果没有安装，系统会：
- 自动跳过向量存储
- 显示警告信息
- 继续正常工作（只是没有语义搜索）

**检查ChromaDB是否可用**:
```python
try:
    from lingnexus.storage.vector import VectorDB
    print("✅ ChromaDB可用")
except ImportError:
    print("⚠️ ChromaDB未安装，向量搜索功能不可用")
```

### 调试技巧

1. **查看爬虫返回的原始数据**:
   ```python
   scraper = ClinicalTrialsGovScraper()
   trials = scraper.search_trials("semaglutide", max_results=1)
   import json
   print(json.dumps(trials[0], indent=2, ensure_ascii=False))
   ```

2. **测试数据库保存**:
   ```python
   db = StructuredDB()
   db.save_trial(
       raw_data_id="test_id",
       extracted_data={...},
       project_name="测试项目"
   )
   # 检查 data/intelligence.db
   ```

3. **监控任务日志**:
   ```bash
   # 监控任务会输出详细的进度信息
   python -m lingnexus.cli monitor --project "司美格鲁肽"
   ```

---

## 常见问题

### Q: ChromaDB安装失败？

**A**: Windows上ChromaDB需要C++编译器。解决方案：
1. 安装Visual Studio C++ Build Tools
2. 或者跳过ChromaDB，系统仍可正常使用（只是没有向量搜索）

### Q: CDE爬虫无法获取数据？

**A**: CDE网站可能改版。需要：
1. 手动访问CDE网站
2. 使用浏览器开发者工具检查页面元素
3. 更新 `cde_scraper.py` 中的选择器

### Q: 数据库文件在哪里？

**A**:
- 原始数据: `data/raw/{source}/{date}/`
- SQLite数据库: `data/intelligence.db`
- 向量数据库: `data/vectordb/`

### Q: 如何重新采集数据？

**A**:
```bash
# 方法1: 删除数据库文件后重新采集
rm data/intelligence.db
python -m lingnexus.cli monitor

# 方法2: 只采集特定项目
python -m lingnexus.cli monitor --project "司美格鲁肽"
```

---

## 系统状态

### 已完成 ✅

- ✅ **存储层**: 原始、向量、结构化三层存储
- ✅ **ClinicalTrials.gov爬虫**: 100%完成并测试
- ✅ **监控任务框架**: 完整的采集流程
- ✅ **CLI工具**: 统一的命令行接口
- ✅ **配置管理**: YAML配置文件
- ✅ **端到端测试**: 10条数据成功采集

### 待开发 ⏳

- ⏳ **CDE爬虫**: 需要现场调试
- ⏳ **Insight爬虫**: 需要实现半自动登录
- ⏳ **变化检测**: 对比新旧数据，识别状态变化
- ⏳ **告警系统**: 邮件/Webhook通知
- ⏳ **报告生成**: LLM自动生成分析报告
- ⏳ **Celery集成**: 定时任务自动化
- ⏳ **FastAPI接口**: RESTful API端点

### 已知问题 ⚠️

1. **CDE爬虫选择器**: 需要根据实际网页调整
2. **SQLAlchemy警告**: `declarative_base` 已弃用（不影响功能）
3. **向量数据库**: Windows上ChromaDB安装困难（已设为可选）

---

## 文件索引

### 核心代码

- `lingnexus/cli/__main__.py` - CLI统一入口
- `lingnexus/cli/monitoring.py` - 监控命令
- `lingnexus/scheduler/monitoring.py` - 监控调度器
- `lingnexus/storage/raw.py` - 原始数据存储
- `lingnexus/storage/structured.py` - 结构化数据库
- `lingnexus/storage/vector.py` - 向量数据库

### 爬虫脚本

- `skills/internal/intelligence/scripts/clinical_trials_scraper.py`
- `skills/internal/intelligence/scripts/cde_scraper.py`

### 配置文件

- `config/projects_monitoring.yaml` - 监控项目配置

### 相关文档

- `README.md` - 项目总览
- `docs/architecture.md` - 系统架构
- `docs/cli_guide.md` - CLI详细指南

---

**维护者**: LingNexus开发团队
**最后更新**: 2026-01-05
