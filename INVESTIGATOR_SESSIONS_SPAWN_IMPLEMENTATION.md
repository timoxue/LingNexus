# Investigator 并发执行实现指南

## 概述

本文档说明如何在 Investigator agent 中使用 OpenClaw 原生的 `sessions_spawn` 能力实现并发搜索任务执行。

## 架构更新

### 1. AGENTS.md 配置

已添加 subagents 配置：

```yaml
## subagents
- investigator:
    allowAgents: ["investigator"]
    maxConcurrent: 5
    timeoutSeconds: 60
    cleanup: delete
```

这允许 Investigator 主 agent 生成最多 5 个 Investigator subagent 并发执行任务。

### 2. SOUL.md 执行指南

已更新并发执行部分，使用 sessions_spawn 替代 run_in_background。

## 实现方式

### 主 Agent 工作流

当 Investigator 被激活时：

1. **读取任务列表**
   ```python
   import json
   with open('/workspace/blackboard/Pending_Tasks.json', 'r') as f:
       tasks = json.load(f)
   pending_tasks = [t for t in tasks if t['status'] == 'pending']
   ```

2. **为每个任务生成 subagent**
   ```python
   from openclaw import sessions_spawn

   for task in pending_tasks:
       task_prompt = f"""
       执行搜索任务：
       - 查询词: {task['search_query']}
       - 语言: {task['language']}
       - 数据源: {task['target_source']}
       - 任务ID: {task['task_id']}

       步骤：
       1. 使用 Bash 工具调用搜索网关：
          cd /workspace && python3 skills/global_search_skill.py "{task['search_query']}" "{task['target_source']}"

       2. 将搜索结果转换为 Raw_Evidence 格式：
          {{
            "evidence_id": "E{{timestamp}}_{task['task_id']}_{{index}}",
            "source_task_id": "{task['task_id']}",
            "language": "{task['language']}",
            "region": "{task['region']}",
            "source_url": "{{result_url}}",
            "source_name": "{task['target_source']}",
            "raw_text": "{{full_text}}",
            "crawled_at": "{{iso8601}}",
            "status": "pending_validation"
          }}

       3. 读取现有的 /workspace/blackboard/Raw_Evidence.json
       4. 追加新证据到数组
       5. 写回完整数组到文件

       6. 更新任务状态：
          - 读取 /workspace/blackboard/Pending_Tasks.json
          - 将 task_id={task['task_id']} 的状态改为 "completed"
          - 写回文件
       """

       sessions_spawn(
           task=task_prompt,
           label=f"Search-{task['task_id']}",
           agentId="investigator",
           runTimeoutSeconds=60,
           cleanup="delete"
       )
   ```

3. **等待所有 subagent 完成**
   - OpenClaw 自动管理 subagent 生命周期
   - 每个 subagent 完成后通过 announcement 返回结果
   - 主 agent 收到所有 announcement 后继续

4. **验证结果**
   ```python
   # 检查所有任务是否完成
   with open('/workspace/blackboard/Pending_Tasks.json', 'r') as f:
       tasks = json.load(f)
   completed = [t for t in tasks if t['status'] == 'completed']
   print(f"Completed {len(completed)}/{len(tasks)} tasks")
   ```

### Subagent 工作流

每个 subagent 独立执行：

1. 调用搜索网关获取数据
2. 转换为 Raw_Evidence 格式
3. 写入黑板（需要处理并发写入）
4. 更新任务状态
5. 返回 announcement 给主 agent

## 并发写入黑板的安全性

由于多个 subagent 可能同时写入 `/workspace/blackboard/Raw_Evidence.json`，需要考虑文件锁或原子操作：

### 方案 1：文件锁（推荐）

```python
import json
import fcntl

def append_evidence(evidence_list):
    blackboard_path = '/workspace/blackboard/Raw_Evidence.json'

    with open(blackboard_path, 'r+') as f:
        # 获取文件锁
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

        try:
            # 读取现有数据
            f.seek(0)
            existing_data = json.load(f)

            # 追加新数据
            existing_data.extend(evidence_list)

            # 写回
            f.seek(0)
            f.truncate()
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        finally:
            # 释放锁
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

### 方案 2：每个 subagent 写独立文件

```python
# 每个 subagent 写入独立文件
evidence_file = f'/workspace/blackboard/Raw_Evidence_{task_id}.json'
with open(evidence_file, 'w') as f:
    json.dump(evidence_list, f, indent=2, ensure_ascii=False)

# 主 agent 在所有 subagent 完成后合并
import glob
all_evidence = []
for file in glob.glob('/workspace/blackboard/Raw_Evidence_*.json'):
    with open(file, 'r') as f:
        all_evidence.extend(json.load(f))

with open('/workspace/blackboard/Raw_Evidence.json', 'w') as f:
    json.dump(all_evidence, f, indent=2, ensure_ascii=False)
```

## 性能预期

- **顺序执行**: 5 个任务 × 5 秒 = 25 秒
- **并发执行**: max(5 个任务) ≈ 5-8 秒
- **加速比**: ~3-5x

## 测试验证

运行测试脚本：

```bash
./test-investigator-concurrent.sh
```

预期输出：
- 3 个任务并发执行
- 总耗时 < 10 秒（如果顺序执行需要 ~15 秒）
- 所有任务状态更新为 "completed"
- Raw_Evidence 包含所有搜索结果

## 故障排查

### 问题 1: subagent 无法生成

**症状**: 报错 "Agent investigator is not allowed to spawn subagents"

**解决**: 检查 AGENTS.md 中的 subagents 配置是否正确

### 问题 2: 并发写入导致数据丢失

**症状**: Raw_Evidence 中的证据数量少于预期

**解决**: 使用文件锁或独立文件方案

### 问题 3: subagent 超时

**症状**: 某些任务未完成，状态仍为 "pending"

**解决**: 增加 runTimeoutSeconds 或优化搜索网关性能

## 下一步

1. 测试 3 任务并发执行
2. 测试 5 任务并发执行（满负载）
3. 验证并发写入安全性
4. 测量实际加速比
5. 集成到完整工作流

---

**创建时间**: 2026-03-17
**状态**: 实现完成，待测试验证
