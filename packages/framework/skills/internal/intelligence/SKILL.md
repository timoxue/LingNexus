---
name: intelligence
version: 1.0.0
description: 竞品情报自动采集和监控系统
author: LingNexus
tags: [intelligence, monitoring, scraping, competitive-analysis]
dependencies:
  - playwright
  - beautifulsoup4
  - chromadb
  - sqlalchemy
  - pyyaml
  - requests
---

# 竞品情报智能采集系统

## 功能概述

本skill提供竞品情报的自动采集、存储和监控功能。

### 核心功能

1. **数据采集**：自动爬取CDE、Insight、ClinicalTrials.gov等数据源
2. **数据存储**：全量保存原始数据，支持向量检索和结构化查询
3. **变化监控**：每日自动监控，检测重要状态变化
4. **智能告警**：发现关键变化立即通知
5. **API接口**：提供RESTful API供外部系统查询

## 使用方法

### CLI命令（推荐）

```bash
# 监控所有项目
uv run python -m lingnexus.cli monitor

# 监控单个项目
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# 查看监控状态
uv run python -m lingnexus.cli status

# 生成报告
uv run python -m lingnexus.cli report --project "司美格鲁肽" --type weekly
```

### Python脚本调用

```python
from lingnexus.scheduler.monitoring import DailyMonitoringTask

# 创建监控任务
task = DailyMonitoringTask()

# 执行监控
results = task.run()

# 查看结果
for project, data in results.items():
    print(f"{project}: 采集到 {len(data)} 条数据")
```

## 监控项目配置

在 `config/projects_monitoring.yaml` 中配置监控项目。

## 数据存储

### 原始数据
- 路径：`data/raw/{source}/{date}/`
- 格式：完整HTML/JSON
- 用途：数据溯源、重新提取

### 向量数据库
- 路径：`data/vectordb/`
- 技术：ChromaDB
- 用途：LLM检索、语义搜索

### 结构化数据
- 路径：`data/intelligence.db`
- 技术：SQLite
- 用途：API查询、前端展示

## 支持的数据源

### 1. CDE（中国药品审评中心）
- 网址：http://www.chinadrugtrials.org.cn
- 数据：国内临床试验登记
- 采集频率：每日

### 2. ClinicalTrials.gov
- 网址：https://clinicaltrials.gov
- 数据：国际临床试验
- 采集频率：每日

### 3. Insight（丁香园数据库）
- 网址：https://db.dxy.cn
- 数据：IND/NDA/ANDA申报进度
- 采集频率：每日
- 注意：需要手动登录一次

## 工具脚本

### scripts/cde_scraper.py

CDE网站爬虫，采集国内临床试验数据。

### scripts/insight_scraper.py

Insight数据库爬虫，采集申报进度数据。

### scripts/clinical_trials_scraper.py

ClinicalTrials.gov爬虫，采集国际临床试验数据。

### scripts/storage.py

数据存储辅助脚本。

## 注意事项

### 1. Insight登录

Insight需要验证码，首次使用需要手动登录。

### 2. 反爬虫

建议：
- 添加随机延迟（1-3秒）
- 使用代理池（可选）
- 遵守robots.txt
- 设置合理的请求频率

### 3. 数据准确性

定期人工抽查采集的数据。

## 故障排查

### 问题：爬虫失败

```bash
# 查看日志
cat logs/*.log

# 测试单个爬虫
uv run python -m lingnexus.scheduler test
```

### 问题：向量数据库无法连接

```bash
# 重置向量数据库
rm -rf data/vectordb/
```

## 示例

### 监控司美格鲁肽

```python
from lingnexus.scheduler.monitoring import DailyMonitoringTask

task = DailyMonitoringTask()
results = task.run(project_names=["司美格鲁肽"])

# 查看数据
semaglutide_data = results.get("司美格鲁肽")
print(f"采集到 {len(semaglutide_data)} 条新数据")
```

### 查询历史数据

```python
from lingnexus.storage.vector import VectorDB

vectordb = VectorDB()
results = vectordb.search(
    query="司美格鲁肽III期临床试验",
    n_results=10
)

for result in results:
    print(f"{result['metadata']['source']}: {result['document']}")
```

## 参考资料

- [CDE网站使用指南](references/cde_guide.md)
- [数据源说明](references/data_sources.md)
- [API文档](../../docs/api_reference.md)

## 版本历史

- **v1.0.0** (2026-01-05): 初始版本
