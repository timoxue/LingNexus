# LingNexus Framework

多智能体系统框架，专为医药行业设计。

## 特性

- **渐进式披露机制**: 高效管理大量 Skills，最小化 Token 使用
- **三层存储架构**: 原始数据、结构化数据库、向量数据库
- **监控系统**: 内置竞争情报数据采集和分析
- **合规支持**: FDA 21 CFR Part 11、GCP 审计日志
- **Claude Skills 兼容**: 完全兼容 Claude Skills 格式

## 安装

```bash
pip install lingnexus-framework
```

## 快速开始

```python
from lingnexus import create_progressive_agent

# 创建智能体
agent = create_progressive_agent(
    model_name="qwen-max",
    temperature=0.3,
)

# 使用智能体
from agentscope.message import Msg

response = agent(Msg(name="user", content="你好"))
print(response.content)
```

## 文档

- [快速开始](https://docs.lingnexus.com/framework/getting-started)
- [API 参考](https://docs.lingnexus.com/framework/api)
- [架构设计](https://docs.lingnexus.com/development/architecture)

## 可选依赖

```bash
# 监控系统（ClinicalTrials.gov, CDE 爬虫）
pip install "lingnexus-framework[monitoring]"

# 向量数据库（语义搜索）
pip install "lingnexus-framework[vector]"

# 开发工具
pip install "lingnexus-framework[dev]"

# 全部功能
pip install "lingnexus-framework[all]"
```

## CLI 使用

```bash
# 监控系统
lingnexus monitor --project "司美格鲁肽"

# 查看状态
lingnexus status

# 数据库查询
lingnexus db --project "司美格鲁肽"

# 语义搜索
lingnexus search "关键词"
```

## 许可证

MIT License

## 支持

- 文档: https://docs.lingnexus.com
- Issues: https://github.com/your-org/LingNexus/issues
- 邮箱: support@lingnexus.com
