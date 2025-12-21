## LingNexus Skill 能力地图 v0.1

> 本文档用于梳理当前 LingNexus 平台中已经存在的核心 Skill 能力，按业务域（Intelligence / BD / RD）和能力类型（检索 / 分析 / 生成）归类，作为后续“插件（Plugin）生态”建设的基础能力地图。

---

### 一、文档目标与适用范围

- **文档目标**：
  - 明确当前已经实现的 Skill 能力，以及它们在业务链路中的位置；
  - 为后续“Skill → Plugin”封装提供统一视图（哪些能直接做成插件、哪些需要组合）；
  - 作为阶段 0 的成果沉淀，方便团队成员快速了解“我们已经有什么”。
- **不包含内容**：
  - 不涉及插件运行时（plugin_runtime）的实现细节；
  - 不涉及 Plugin Store / Web 操作台的 UI 设计；
  - 不对未来 Skill 做穷举，只关注当前代码中已存在的代表性能力。

---

### 二、Intelligence 域 Skill 能力

#### 2.1 能力清单

| Skill 名称 | 完整 ID | 所在文件 | 能力类型 | 上游调用者 | 下游依赖 | 典型输入 | 典型输出 | 插件候选性 |
|-----------|---------|----------|----------|-----------|----------|----------|----------|------------|
| 资讯检索技能 | `intel.fetch_news` | `shared/skills/intelligence/fetch_news.py` | 检索 / 聚合 | `RetrievalAgent.fetch_news_for_topic`（情报订阅日报，`DailyDigestWorkflow`） | `ESClient`（`local_file` / `remote_es`）、`pharma_news` 索引 | `topic_name`，`keywords[]`，`max_items` | `data`: 原始资讯 `dict[]`（字段与 `pharma_news.json` 对齐） | **高**：可以自然演变成“资讯速览/快讯插件”的底层能力 |
| 日报生成技能 | `intel.generate_daily_digest` | `shared/skills/intelligence/daily_digest.py` | 生成 / 总结 | `AnalysisAgent.build_digest`（情报订阅日报） | `PromptManager`（`intelligence_daily_digest_v1`），`llm_manager` | `topic_name`，`topic_description`，`news_items_text`，`role` | `data`: 订阅日报完整文本 | **高**：非常适合作为“订阅日报插件”的核心能力 |

#### 2.2 在业务链路中的位置

- **订阅日报主链路**（已实现）：
  - Workflow：`DailyDigestWorkflow.run_daily_digest`；
  - Agent：
    - `RetrievalAgent.fetch_news_for_topic` → Skill `intel.fetch_news`；
    - `AnalysisAgent.build_digest` → Skill `intel.generate_daily_digest`；
  - API：`POST /v1/internal/daily_digest`；
  - 数据来源：`shared/storage/es_client.py`（`local_file` / `remote_es`）+ 本地 `data/pharma_news.json`。
- **未来插件示例（Intelligence 域）**：
  - 「资讯速览」插件：基于 `intel.fetch_news`，对单一主题做 Top-N 资讯列表输出；
  - 「订阅日报 Quick Run」插件：直接封装 `run_daily_digest` + `intel.generate_daily_digest`，允许业务用户选择主题和角色，一键生成日报。

---

### 三、BD 域 Skill 能力

#### 3.1 能力清单

| Skill 名称 | 完整 ID | 所在文件 | 能力类型 | 上游调用者 | 下游依赖 | 典型输入 | 典型输出 | 插件候选性 |
|-----------|---------|----------|----------|-----------|----------|----------|----------|------------|
| BD 线索评估技能 | `bd.lead_qualification` | `shared/skills/bd/lead_qualification.py` | 分析 / 决策支持 | `run_bd_pipeline`（`core_agents/bd_service/workflows/bd_workflow.py`） | `PromptManager`（`shared/prompts/bd.yaml` 中评估 Prompt），`llm_manager`（Qwen 等） | `target`（项目/合作机会名），`context`（背景描述） | `data`: 线索评估总结文本（可包含评分、风险点、建议） | **很高**：一个很自然的“BD 机会评估插件”，适合业务侧直接调用 |

#### 3.2 在业务链路中的位置

- **BD 主链路**（当前版本）：
  - Workflow：`run_bd_pipeline(request: BDRequest) -> BDResponse`；
  - Skill 调用：
    - 从 Skill Registry 获取 `bd.lead_qualification`；
    - 构造输入模型，调用 `skill.execute(input_data)`；
    - 将 Skill 输出填入 `BDResponse.summary`（以及后续扩展字段，如 `recommendations`）。
  - API：`POST /bd/analyze`。
- **未来插件示例（BD 域）**：
  - 「BD 机会评估」插件：
    - 输入：目标公司/项目名称 + 背景描述；
    - 内部调用 Skill `bd.lead_qualification`，产出结构化的评估报告；
    - 以 Web 界面/IM 机器人形式返回给 BD 经理。

---

### 四、RD 域 Skill 能力

#### 4.1 能力清单

| Skill 名称 | 完整 ID | 所在文件 | 能力类型 | 上游调用者 | 下游依赖 | 典型输入 | 典型输出 | 插件候选性 |
|-----------|---------|----------|----------|-----------|----------|----------|----------|------------|
| 化合物分析技能 | `rd.compound_analysis` | `shared/skills/rd/compound_analysis.py` | 分析 / 评估 | `run_rd_pipeline`（`core_agents/rd_service/workflows/rd_workflow.py`） | `PromptManager`（`shared/prompts/rd.yaml` 中化合物分析 Prompt），`llm_manager`（DeepSeek 等） | `compound`（化合物 ID/代号），`context`（机制、适应症、开发阶段等背景信息） | `data`: 化合物分析总结文本（作用机制、安全性、竞品格局、机会/风险） | **很高**：可以做成“化合物一键评估插件”，面向研究员使用 |

#### 4.2 在业务链路中的位置

- **RD 主链路**（当前版本）：
  - Workflow：`run_rd_pipeline(request: RDRequest) -> RDResponse`；
  - Skill 调用：
    - 从 Skill Registry 获取 `rd.compound_analysis`；
    - 调用 `skill.execute(input_data)` 获取分析结果；
    - 将结果写入 `RDResponse.summary`。
  - API：`POST /rd/analyze`。
- **未来插件示例（RD 域）**：
  - 「化合物一键分析」插件：
    - 输入：化合物代号 + 背景描述；
    - 输出：用于项目立项/评审的标准化分析报告（可插入到 Word/PPT 中）。

---

### 五、跨域 Skill 关系与映射

#### 5.1 Workflow / Agent → Skill 映射表

| 上游 Workflow/Agent | 调用的 Skill | 输出给谁 | 说明 |
|---------------------|--------------|---------|------|
| `DailyDigestWorkflow.run_daily_digest` | `intel.fetch_news` | `AnalysisAgent`（作为 `NewsItem[]`） | 针对每个 Topic 进行资讯检索，得到候选资讯集合 |
| `AnalysisAgent.build_digest` | `intel.generate_daily_digest` | `DailyDigestItem.digest_summary` | 按角色和主题生成订阅日报完整文本 |
| `run_bd_pipeline` | `bd.lead_qualification` | `BDResponse.summary` | 对指定 BD 机会进行评估和建议输出 |
| `run_rd_pipeline` | `rd.compound_analysis` | `RDResponse.summary` | 对指定化合物进行多维度分析 |

#### 5.2 对未来插件设计的意义

- **Skill 是 Plugin 的能力颗粒度单位**：
  - 插件不直接操作 ES/LLM，而是组合调用一个或多个 Skill；
  - 这样可以沿用当前的权限边界和数据访问封装。
- **Plugin 更偏“场景入口 + 参数约定 + 输出格式”**：
  - 如「订阅日报 Quick Run」插件，可以视为：
    - 上游入口：Plugin Runtime / Web 表单 / IM 指令；
    - 核心能力：`intel.fetch_news` + `intel.generate_daily_digest`；
    - 输出载体：邮件/IM 消息/文档片段。

---

### 六、阶段 0 小结与后续工作

#### 6.1 阶段 0 小结

- 已完成：
  - 梳理 Intelligence / BD / RD 三个业务域的核心 Skill，并建立跨域能力地图；
  - 明确每个 Skill 的位置：**所在文件 → 上游调用者 → 下游依赖 → 典型输入输出**；
  - 评估了“是否适合作为插件能力”的初步结论，为后续 Plugin 设计提供参考。

#### 6.2 后续阶段建议

- **阶段 1：Plugin 标准与运行时 MVP 设计**
  - 固化 `plugin_manifest.json` 规范：`plugin_id`、`version`、`required_skills`、`input_schema`、`output_schema`、`permissions` 等；
  - 设计 `plugin_runtime` 的最小接口：`/plugins/{plugin_id}/invoke`、`/plugins` 列表等；
  - 明确插件如何在内部调用现有 Skill 或 core_agents API。
- **阶段 2：选取 1–2 个代表性插件进行 PoC**
  - 如「订阅日报 Quick Run」「BD 机会评估」「化合物一键分析」，各选一条链路做成可演示插件；
  - 在不破坏现有服务的前提下，引入 Plugin Runtime 作为“上层壳”。

> 本文档会随着新 Skill 的加入和 Plugin 生态的演进持续更新，当前版本为 **v0.1**，覆盖了 LingNexus `0.0.1` 版本中已经落地的代表性技能能力。