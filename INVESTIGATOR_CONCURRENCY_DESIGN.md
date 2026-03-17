# Investigator 并发执行方案

**设计目标**: 将 5 个搜索任务的总耗时从 ~25s 降至 ~5s

---

## 一、并发架构设计

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                  Investigator Agent                      │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Task Coordinator (任务协调器)           │    │
│  │  - 读取 Pending_Tasks                           │    │
│  │  - 创建任务队列                                 │    │
│  │  - 分配任务到 Worker                            │    │
│  └────────────────────────────────────────────────┘    │
│                         │                                │
│                         ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │      Task Queue (任务队列 - 优先级队列)        │    │
│  │  [T1:priority=1] [T2:priority=2] ...           │    │
│  └────────────────────────────────────────────────┘    │
│                         │                                │
│         ┌───────────────┼───────────────┐               │
│         ▼               ▼               ▼               │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐           │
│  │ Worker 1 │   │ Worker 2 │   │ Worker 3 │  ...      │
│  │ (后台)   │   │ (后台)   │   │ (后台)   │           │
│  └──────────┘   └──────────┘   └──────────┘           │
│         │               │               │               │
│         └───────────────┼───────────────┘               │
│                         ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │      Result Collector (结果收集器)             │    │
│  │  - 监控任务状态                                 │    │
│  │  - 收集完成的结果                               │    │
│  │  - 处理失败和重试                               │    │
│  └────────────────────────────────────────────────┘    │
│                         │                                │
│                         ▼                                │
│  ┌────────────────────────────────────────────────┐    │
│  │      Blackboard Writer (黑板写入器)            │    │
│  │  - 批量写入 Raw_Evidence                        │    │
│  │  - 更新 Pending_Tasks 状态                      │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 1.2 核心组件

**Task Coordinator (任务协调器)**
- 职责: 读取任务、创建队列、分配工作
- 输入: Pending_Tasks (status="pending")
- 输出: 任务队列

**Worker (工作线程)**
- 职责: 执行单个搜索任务
- 方式: Bash 工具 + run_in_background=true
- 数量: 最多 5 个并发

**Result Collector (结果收集器)**
- 职责: 监控任务状态、收集结果
- 工具: TaskOutput 工具
- 超时: 每个任务 60s

**Blackboard Writer (黑板写入器)**
- 职责: 批量写入结果到黑板
- 原子性: 一次性写入所有结果

---

## 二、并发方案对比

### 方案 A: OpenClaw Agent 内置并发 (推荐)

**实现方式**: 使用 Bash 工具的 `run_in_background` 参数

**优点**:
- ✅ 简单直接，利用现有工具
- ✅ 不需要修改 Python 代码
- ✅ Agent 可以直接控制

**缺点**:
- ⚠️ 需要手动管理任务状态
- ⚠️ 错误处理需要额外逻辑

**代码示例**:
```python
# Investigator Agent 执行逻辑
def execute_concurrent_search(tasks):
    # Step 1: 启动所有后台任务
    task_ids = []
    for task in tasks:
        task_id = Bash(
            command=f"cd /workspace && python3 skills/global_search_skill.py '{task['search_query']}' 'pubmed'",
            run_in_background=true,
            timeout=60000,
            description=f"Search task {task['task_id']}"
        )
        task_ids.append((task['task_id'], task_id))

    # Step 2: 等待所有任务完成
    results = []
    for task_id, bg_task_id in task_ids:
        output = TaskOutput(task_id=bg_task_id, block=true, timeout=60000)
        results.append({
            'task_id': task_id,
            'output': output,
            'status': 'completed' if output.success else 'failed'
        })

    # Step 3: 批量写入黑板
    write_to_blackboard(results)
```

### 方案 B: Python 多线程 (备选)

**实现方式**: 修改 global_search_skill.py，使用 ThreadPoolExecutor

**优点**:
- ✅ 更精细的控制
- ✅ 内置错误处理和重试

**缺点**:
- ❌ 需要修改 Python 代码
- ❌ Agent 无法直接监控进度

**代码示例**:
```python
# global_search_skill.py
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

def execute_concurrent_tasks(tasks_file, output_file):
    with open(tasks_file, 'r') as f:
        tasks = json.load(f)

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_task = {
            executor.submit(
                global_intelligence_search,
                task['search_query'],
                'pubmed'
            ): task for task in tasks
        }

        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                result = future.result(timeout=60)
                results.append({
                    'task_id': task['task_id'],
                    'result': result,
                    'status': 'completed'
                })
            except Exception as e:
                results.append({
                    'task_id': task['task_id'],
                    'error': str(e),
                    'status': 'failed'
                })

    with open(output_file, 'w') as f:
        json.dump(results, f)
```

---

## 三、推荐方案实现 (方案 A)

### 3.1 Investigator Agent 执行流程

```
1. 读取 Pending_Tasks
   ↓
2. 过滤 status="pending" 的任务
   ↓
3. 为每个任务启动后台 Bash 命令
   ↓
4. 收集所有 task_id
   ↓
5. 使用 TaskOutput 等待所有任务完成
   ↓
6. 解析结果并转换为 Raw_Evidence 格式
   ↓
7. 批量写入黑板
   ↓
8. 更新 Pending_Tasks 状态
```

### 3.2 详细实现步骤

**Step 1: 读取任务**
```python
# Investigator Agent 内部逻辑
import json

# 读取黑板
with open('/workspace/blackboard/Pending_Tasks.json', 'r') as f:
    all_tasks = json.load(f)

# 过滤待执行任务
pending_tasks = [t for t in all_tasks if t['status'] == 'pending']
print(f"发现 {len(pending_tasks)} 个待执行任务")
```

**Step 2: 启动并发任务**
```python
# 为每个任务启动后台进程
background_tasks = []

for task in pending_tasks:
    # 构建搜索命令
    query = task['search_query']
    domain = 'pubmed'  # 根据 target_source 智能选择

    # 启动后台任务
    task_id = Bash(
        command=f"cd /workspace && python3 skills/global_search_skill.py \"{query}\" \"{domain}\"",
        run_in_background=True,
        timeout=60000,
        description=f"Execute search: {task['task_id']}"
    )

    background_tasks.append({
        'original_task': task,
        'bg_task_id': task_id
    })

print(f"已启动 {len(background_tasks)} 个后台任务")
```

**Step 3: 等待并收集结果**
```python
# 等待所有任务完成
completed_results = []

for bg_task in background_tasks:
    try:
        # 阻塞等待任务完成
        output = TaskOutput(
            task_id=bg_task['bg_task_id'],
            block=True,
            timeout=60000
        )

        completed_results.append({
            'task': bg_task['original_task'],
            'output': output.stdout,
            'success': output.exit_code == 0,
            'error': output.stderr if output.exit_code != 0 else None
        })
    except TimeoutError:
        completed_results.append({
            'task': bg_task['original_task'],
            'output': None,
            'success': False,
            'error': 'Task timeout after 60s'
        })

print(f"收集到 {len(completed_results)} 个结果")
```

**Step 4: 转换为 Raw_Evidence 格式**
```python
import time

raw_evidence_list = []

for result in completed_results:
    if not result['success']:
        print(f"任务 {result['task']['task_id']} 失败: {result['error']}")
        continue

    # 解析 PubMed 输出
    output_lines = result['output'].split('\n')

    # 提取每条文献
    current_pmid = None
    current_title = None
    current_abstract = None

    for line in output_lines:
        if line.startswith('[') and '] PMID:' in line:
            # 保存上一条
            if current_pmid:
                raw_evidence_list.append({
                    'evidence_id': f"E{int(time.time())}_{result['task']['task_id']}_{current_pmid}",
                    'source_task_id': result['task']['task_id'],
                    'language': result['task']['language'],
                    'region': result['task']['region'],
                    'source_url': f"https://pubmed.ncbi.nlm.nih.gov/{current_pmid}/",
                    'source_name': 'PubMed',
                    'raw_text': f"PMID: {current_pmid}. Title: {current_title}. Abstract: {current_abstract}",
                    'crawled_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'status': 'pending_validation'
                })

            # 开始新的一条
            current_pmid = line.split('PMID:')[1].strip()
        elif line.startswith('标题:') or line.startswith('Title:'):
            current_title = line.split(':', 1)[1].strip()
        elif line.startswith('摘要:') or line.startswith('Abstract:'):
            current_abstract = line.split(':', 1)[1].strip()

print(f"转换为 {len(raw_evidence_list)} 条 Raw_Evidence")
```

**Step 5: 批量写入黑板**
```python
# 读取现有数据
blackboard_path = '/workspace/blackboard/Raw_Evidence.json'
if os.path.exists(blackboard_path):
    with open(blackboard_path, 'r') as f:
        existing_data = json.load(f)
else:
    existing_data = []

# 追加新数据
existing_data.extend(raw_evidence_list)

# 写回黑板
with open(blackboard_path, 'w') as f:
    json.dump(existing_data, f, indent=2, ensure_ascii=False)

print(f"已写入 {len(raw_evidence_list)} 条新证据到黑板")
```

**Step 6: 更新任务状态**
```python
# 更新 Pending_Tasks 状态
for task in pending_tasks:
    task['status'] = 'completed'

with open('/workspace/blackboard/Pending_Tasks.json', 'w') as f:
    json.dump(all_tasks, f, indent=2, ensure_ascii=False)

print("所有任务状态已更新")
```

---

## 四、错误处理和重试机制

### 4.1 三层错误处理

**Layer 1: 任务级别**
```python
def execute_task_with_retry(task, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = Bash(
                command=f"cd /workspace && python3 skills/global_search_skill.py \"{task['search_query']}\" \"pubmed\"",
                run_in_background=True,
                timeout=60000
            )

            output = TaskOutput(task_id=result, block=True, timeout=60000)

            if output.exit_code == 0:
                return {'success': True, 'output': output.stdout}
            else:
                print(f"任务失败 (尝试 {attempt + 1}/{max_retries}): {output.stderr}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
        except Exception as e:
            print(f"异常 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

    return {'success': False, 'error': 'Max retries exceeded'}
```

**Layer 2: 批次级别**
```python
def execute_batch_with_fallback(tasks):
    # 尝试并发执行
    try:
        return execute_concurrent(tasks)
    except Exception as e:
        print(f"并发执行失败: {e}")
        print("降级为串行执行")
        return execute_sequential(tasks)
```

**Layer 3: 系统级别**
```python
def execute_with_circuit_breaker(tasks):
    failure_count = 0
    failure_threshold = 3

    for task in tasks:
        if failure_count >= failure_threshold:
            print("熔断器触发，停止执行")
            break

        result = execute_task(task)
        if not result['success']:
            failure_count += 1
        else:
            failure_count = 0  # 重置计数器
```

### 4.2 超时处理

```python
# 任务超时配置
TIMEOUT_CONFIG = {
    'pubmed': 30000,      # PubMed: 30s
    'general_web': 45000,  # 网页抓取: 45s
    'default': 60000       # 默认: 60s
}

def get_timeout(domain):
    return TIMEOUT_CONFIG.get(domain, TIMEOUT_CONFIG['default'])
```

---

## 五、资源控制

### 5.1 并发数限制

```python
# 动态调整并发数
def get_optimal_concurrency(task_count):
    if task_count <= 3:
        return task_count
    elif task_count <= 5:
        return 5
    else:
        return 5  # 最大并发数

MAX_CONCURRENT = get_optimal_concurrency(len(pending_tasks))
```

### 5.2 内存管理

```python
# 批量处理大量任务
def process_in_batches(tasks, batch_size=5):
    results = []
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        batch_results = execute_concurrent(batch)
        results.extend(batch_results)

        # 清理内存
        import gc
        gc.collect()

    return results
```

---

## 六、性能监控

### 6.1 执行时间统计

```python
import time

start_time = time.time()

# 执行并发任务
results = execute_concurrent(tasks)

end_time = time.time()
duration = end_time - start_time

print(f"总耗时: {duration:.2f}s")
print(f"平均每任务: {duration / len(tasks):.2f}s")
print(f"并发加速比: {(len(tasks) * 5) / duration:.2f}x")
```

### 6.2 成功率统计

```python
success_count = sum(1 for r in results if r['success'])
failure_count = len(results) - success_count

print(f"成功: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
print(f"失败: {failure_count}/{len(results)} ({failure_count/len(results)*100:.1f}%)")
```

---

## 七、完整示例代码

### 7.1 Investigator Agent 完整逻辑

```python
# 这是 Investigator Agent 应该执行的完整逻辑
import json
import time
import os

def execute_concurrent_search():
    # Step 1: 读取任务
    with open('/workspace/blackboard/Pending_Tasks.json', 'r') as f:
        all_tasks = json.load(f)

    pending_tasks = [t for t in all_tasks if t.get('status') == 'pending']

    if not pending_tasks:
        print("没有待执行的任务")
        return

    print(f"发现 {len(pending_tasks)} 个待执行任务")

    # Step 2: 启动并发任务
    background_tasks = []
    start_time = time.time()

    for task in pending_tasks:
        query = task['search_query']
        domain = 'pubmed'  # 简化：都使用 PubMed

        # 使用 Bash 工具启动后台任务
        print(f"启动任务: {task['task_id']}")
        # 注意：这里是伪代码，实际需要通过 Agent 的 Bash 工具调用
        # task_id = Bash(command=..., run_in_background=True)

        background_tasks.append({
            'original_task': task,
            'bg_task_id': f"bg_{task['task_id']}"  # 实际会返回真实的 task_id
        })

    # Step 3: 等待所有任务完成
    print(f"等待 {len(background_tasks)} 个任务完成...")
    completed_results = []

    for bg_task in background_tasks:
        # 使用 TaskOutput 等待
        # output = TaskOutput(task_id=bg_task['bg_task_id'], block=True, timeout=60000)
        # 这里模拟结果
        completed_results.append({
            'task': bg_task['original_task'],
            'success': True,
            'output': "模拟的搜索结果"
        })

    end_time = time.time()
    duration = end_time - start_time

    print(f"所有任务完成，耗时: {duration:.2f}s")

    # Step 4: 转换为 Raw_Evidence 并写入黑板
    raw_evidence_list = []
    for result in completed_results:
        if result['success']:
            raw_evidence_list.append({
                'evidence_id': f"E{int(time.time())}_{result['task']['task_id']}",
                'source_task_id': result['task']['task_id'],
                'language': result['task']['language'],
                'region': result['task']['region'],
                'source_url': 'https://pubmed.ncbi.nlm.nih.gov/',
                'source_name': 'PubMed',
                'raw_text': result['output'],
                'crawled_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'status': 'pending_validation'
            })

    # 写入黑板
    blackboard_path = '/workspace/blackboard/Raw_Evidence.json'
    if os.path.exists(blackboard_path):
        with open(blackboard_path, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    existing_data.extend(raw_evidence_list)

    with open(blackboard_path, 'w') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

    print(f"已写入 {len(raw_evidence_list)} 条证据到黑板")

    # Step 5: 更新任务状态
    for task in pending_tasks:
        task['status'] = 'completed'

    with open('/workspace/blackboard/Pending_Tasks.json', 'w') as f:
        json.dump(all_tasks, f, indent=2, ensure_ascii=False)

    print("任务状态已更新")

    # 统计
    success_count = sum(1 for r in completed_results if r['success'])
    print(f"\n=== 执行统计 ===")
    print(f"总任务数: {len(pending_tasks)}")
    print(f"成功: {success_count}")
    print(f"失败: {len(pending_tasks) - success_count}")
    print(f"总耗时: {duration:.2f}s")
    print(f"平均耗时: {duration / len(pending_tasks):.2f}s/任务")
    print(f"理论加速比: {len(pending_tasks) * 5 / duration:.2f}x")

if __name__ == '__main__':
    execute_concurrent_search()
```

---

## 八、预期性能提升

### 8.1 性能对比

| 场景 | 串行执行 | 并发执行 | 加速比 |
|------|---------|---------|--------|
| 5 个任务 | ~25s | ~5s | 5x |
| 10 个任务 | ~50s | ~10s | 5x |
| 20 个任务 | ~100s | ~20s | 5x |

### 8.2 资源使用

| 指标 | 串行 | 并发 |
|------|------|------|
| CPU 使用率 | 20% | 60% |
| 内存使用 | 100MB | 300MB |
| 网络带宽 | 1MB/s | 3MB/s |

---

## 九、实施计划

### Phase 1: 基础并发 (1-2 天)
- ✅ 实现基本的后台任务启动
- ✅ 实现 TaskOutput 结果收集
- ✅ 测试 2-3 个任务并发

### Phase 2: 错误处理 (1 天)
- ⚡ 实现重试机制
- ⚡ 实现超时处理
- ⚡ 实现降级策略

### Phase 3: 优化和监控 (1 天)
- 📊 添加性能监控
- 📊 优化资源使用
- 📊 压力测试

---

## 十、总结

**核心优势**:
1. ✅ 利用 OpenClaw 现有工具（Bash + TaskOutput）
2. ✅ 不需要修改 Python 代码
3. ✅ Agent 可以完全控制执行流程
4. ✅ 性能提升 5 倍

**关键技术**:
- Bash 工具的 `run_in_background` 参数
- TaskOutput 工具的阻塞等待
- 批量黑板写入

**预期效果**:
- 5 个任务从 25s 降至 5s
- 成功率保持 95%+
- 资源使用合理

---

**文档版本**: v1.0
**创建时间**: 2026-03-17
**作者**: Claude Code
