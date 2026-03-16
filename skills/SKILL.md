---
name: global-intelligence-search
description: 企业级全局情报搜索网关。支持 PubMed 医学文献检索和通用网页抓取。这是 Investigator Agent 唯一合法的外部信息获取武器。
allowed-tools: Bash(python:skills/global_search_skill.py)
---

# 全局情报搜索网关 (Global Intelligence Search)

## 核心能力

这是一个三层解耦的企业级搜索架构：
- **L0 网关层**：智能路由 + 兜底容错
- **L1 引擎层**：医疗数据库引擎 + 浏览器引擎
- **L2 解析层**：HTML 清洗 + 文本提取

## 使用方法

### 命令格式
```bash
python skills/global_search_skill.py "<query>" "<domain>"
```

### 参数说明
- `query`: 搜索关键词（PubMed）或目标 URL（通用网页）
- `domain`: 搜索域，必须为以下之一：
  - `pubmed` - 检索 PubMed 医学文献数据库
  - `general_web` - 抓取通用网页内容

## 使用场景

### 场景 1：检索医学文献
当你需要查阅严谨的医学文献、临床试验数据、药物研发信息时：

```bash
python skills/global_search_skill.py "PROTAC BRD4 degradation" "pubmed"
python skills/global_search_skill.py "molecular glue CDK inhibitor" "pubmed"
python skills/global_search_skill.py "靶向蛋白降解 LYTAC" "pubmed"
```

**返回内容**：
- PMID（PubMed ID）
- 文章标题
- 摘要（自动截断至 500 字符）
- 最多返回 10 条结果

### 场景 2：抓取开源网页
当你需要从公开网站获取数据（专利数据库、公司官网、新闻报道）时：

```bash
python skills/global_search_skill.py "https://clinicaltrials.gov/study/NCT12345678" "general_web"
python skills/global_search_skill.py "https://www.fda.gov/drugs/new-drugs" "general_web"
```

**返回内容**：
- 清洗后的纯文本（移除 script/style/nav 等非正文标签）
- 自动截断至 8000 字符
- 15 秒超时保护

## 容错保障

所有三层（L0/L1/L2）均采用极致容错设计：
- ✅ 网络超时自动捕获
- ✅ 403/反爬自动降级
- ✅ 解析失败返回错误字符串
- ✅ 绝不向上抛出异常导致容器崩溃

## 环境要求

### Python 依赖
```bash
pip install beautifulsoup4 biopython
```

### 环境变量
```bash
export NCBI_EMAIL="your_email@example.com"  # PubMed API 必需
```

## 示例输出

### PubMed 检索示例
```
=== PubMed 检索结果 ===
关键词: PROTAC BRD4

[1] PMID: 12345678
标题: Targeted protein degradation by PROTACs
摘要: Proteolysis-targeting chimeras (PROTACs) are heterobifunctional molecules...

[2] PMID: 87654321
标题: BRD4 degradation in cancer therapy
摘要: BRD4 is a key epigenetic reader protein...
```

### 网页抓取示例
```
=== 网页抓取结果 ===
URL: https://example.com

Clinical Trial Information
Study Title: Phase I Study of XYZ-123
Status: Recruiting
Condition: Solid Tumors
Intervention: XYZ-123 (PROTAC)
...
```

## 严格使用规则

⚠️ **这是 Investigator Agent 唯一合法的外部信息获取工具**

1. **必须根据任务精准选择 domain**：
   - 医学文献 → `pubmed`
   - 网页数据 → `general_web`

2. **禁止行为**：
   - ❌ 不得使用其他未授权的网络工具
   - ❌ 不得对返回结果进行总结或改写
   - ❌ 不得过滤或删除原始信息

3. **并发执行**：
   - 支持多任务并发调用
   - 每个任务独立超时控制
   - 互不阻塞
