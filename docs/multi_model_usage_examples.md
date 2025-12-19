# 多模型使用示例

本文件展示如何在 LingNexus 项目中使用 DeepSeek、Qwen 和 Gemini 三种大模型。

## 1. 基础调用示例

```python
from shared.models.llm_manager import llm_manager

# 使用 DeepSeek（默认模型）
response = await llm_manager.chat(
    messages=[
        {"role": "system", "content": "你是一个医药领域的专家"},
        {"role": "user", "content": "介绍一下阿司匹林的作用机制"}
    ]
)
print(f"DeepSeek 回复: {response}")

# 使用 Qwen
response = await llm_manager.chat(
    messages=[
        {"role": "user", "content": "什么是靶向药物？"}
    ],
    model_name="qwen"
)
print(f"Qwen 回复: {response}")

# 使用 Gemini
response = await llm_manager.chat(
    messages=[
        {"role": "user", "content": "解释一下临床试验的四个阶段"}
    ],
    model_name="gemini"
)
print(f"Gemini 回复: {response}")
```

## 2. 在 Workflow 中使用

### intelligence_service 中使用不同模型

```python
# core_agents/intelligence_service/workflows/intel_workflow.py

from shared.models.llm_manager import llm_manager

async def run_intelligence_pipeline(request: IntelligenceRequest) -> IntelligenceResponse:
    """情报分析流程，支持多模型切换。"""
    
    # 根据任务复杂度选择模型
    if request.complexity == "high":
        model_name = "qwen"  # 使用 Qwen Max，适合复杂分析
    elif request.need_multilingual:
        model_name = "gemini"  # Gemini 多语言能力强
    else:
        model_name = "deepseek"  # 默认 DeepSeek，性价比高
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"用户查询：{request.query}"}
    ]
    
    raw_answer = await llm_manager.chat(
        messages=messages,
        model_name=model_name,
        temperature=0.2
    )
    
    # 后续处理...
    return IntelligenceResponse(summary=raw_answer, ...)
```

## 3. 不同模型的特点与使用场景

### DeepSeek
- **优势**: 性价比极高，推理能力强，适合代码生成和逻辑推理
- **适用场景**: 
  - 日常情报分析
  - 文本摘要
  - 数据提取
- **成本**: 低
- **速度**: 快

```python
# 示例：使用 DeepSeek 进行数据提取
response = await llm_manager.chat(
    messages=[
        {"role": "user", "content": """
        从以下文本中提取关键信息：
        临床试验编号：NCT12345678
        药物名称：XX单抗
        适应症：非小细胞肺癌
        """}
    ],
    model_name="deepseek",
    temperature=0.1  # 低温度确保准确性
)
```

### Qwen（通义千问）
- **优势**: 中文能力极强，长文本理解好，知识储备丰富
- **适用场景**:
  - 复杂中文分析
  - 长文档理解
  - 专业领域知识问答
- **成本**: 中等
- **速度**: 中等

```python
# 示例：使用 Qwen 进行复杂医药分析
response = await llm_manager.chat(
    messages=[
        {"role": "system", "content": "你是医药行业分析专家"},
        {"role": "user", "content": """
        分析以下临床数据的意义：
        [长文本中文医药报告...]
        """}
    ],
    model_name="qwen",
    temperature=0.3,
    max_tokens=2000
)
```

### Gemini
- **优势**: 多模态能力，超长上下文（100万+ token），多语言支持好
- **适用场景**:
  - 多语言文档分析
  - 超长文本处理
  - 需要图片理解的任务（未来扩展）
- **成本**: 中等
- **速度**: 较快

```python
# 示例：使用 Gemini 处理多语言文档
response = await llm_manager.chat(
    messages=[
        {"role": "user", "content": """
        Summarize the following clinical trial report in Chinese:
        [英文临床试验报告...]
        """}
    ],
    model_name="gemini",
    temperature=0.5
)
```

## 4. 模型切换策略

### 动态模型选择

```python
async def analyze_with_best_model(query: str, context: str) -> str:
    """根据任务自动选择最佳模型。"""
    
    # 判断语言
    is_chinese = all('\u4e00' <= c <= '\u9fff' for c in query[:10] if c.strip())
    
    # 判断长度
    is_long_text = len(context) > 5000
    
    # 选择模型
    if is_long_text:
        model = "gemini"  # 长文本用 Gemini
    elif is_chinese:
        model = "qwen"    # 中文用 Qwen
    else:
        model = "deepseek"  # 默认 DeepSeek
    
    messages = [
        {"role": "user", "content": f"查询: {query}\n背景: {context}"}
    ]
    
    return await llm_manager.chat(messages, model_name=model)
```

### 多模型投票机制

```python
async def multi_model_consensus(query: str) -> str:
    """使用多个模型投票，提高准确性。"""
    
    models = ["deepseek", "qwen", "gemini"]
    responses = []
    
    for model in models:
        try:
            response = await llm_manager.chat(
                messages=[{"role": "user", "content": query}],
                model_name=model
            )
            responses.append(response)
        except Exception as e:
            logger.error(f"Model {model} failed: {e}")
    
    # 这里可以实现投票逻辑、一致性检查等
    # 简化示例：返回第一个成功的响应
    return responses[0] if responses else "所有模型均失败"
```

## 5. 配置优先级说明

模型调用会按以下优先级查找配置：

1. **api_keys.yaml**（最高优先级，推荐）
   ```yaml
   deepseek:
     api_key: "sk-xxxxx"
     base_url: "https://api.deepseek.com"
     model: "deepseek-chat"
   ```

2. **环境变量**（次优先级）
   ```bash
   export DEEPSEEK_API_KEY="sk-xxxxx"
   export QWEN_API_KEY="sk-xxxxx"
   export GEMINI_API_KEY="xxxxx"
   ```

3. **model_config.yaml**（备用）
   - 如果前两者都没有配置，使用这里的配置
   - 仅提供结构定义和默认参数

## 6. 常见问题

### Q1: 如何临时切换默认模型？

**方法一**：修改 `model_config.yaml`
```yaml
default_llm: qwen  # 改为 qwen
```

**方法二**：在代码中显式指定
```python
response = await llm_manager.chat(messages, model_name="qwen")
```

### Q2: 某个模型调用失败怎么办？

检查顺序：
1. 确认 `api_keys.yaml` 中的 API Key 正确
2. 检查网络连接（特别是 Gemini 需要访问 Google）
3. 查看错误日志
4. 使用备用模型

```python
try:
    response = await llm_manager.chat(messages, model_name="gemini")
except Exception as e:
    logger.error(f"Gemini failed: {e}, falling back to DeepSeek")
    response = await llm_manager.chat(messages, model_name="deepseek")
```

### Q3: 如何统计各模型的使用情况和成本？

在 `llm_manager.py` 的日志中已包含模型信息：

```python
logger.info(
    "Calling LLM",
    extra={
        "provider": provider_name,
        "model": model,
        "temperature": temperature,
    },
)
```

可以通过日志分析工具（如 ELK）统计各模型的调用次数和 Token 消耗。

## 7. 性能对比参考

| 模型 | 中文能力 | 英文能力 | 推理能力 | 速度 | 成本 | 上下文长度 |
|------|---------|---------|---------|------|------|-----------|
| DeepSeek | ★★★★☆ | ★★★★☆ | ★★★★★ | 快 | 低 | 32K |
| Qwen Max | ★★★★★ | ★★★★☆ | ★★★★☆ | 中 | 中 | 30K |
| Gemini 1.5 Pro | ★★★★☆ | ★★★★★ | ★★★★☆ | 快 | 中 | 1M+ |

## 8. 最佳实践建议

1. **开发环境**：优先使用 DeepSeek（快速迭代，成本低）
2. **生产环境**：根据任务类型选择合适模型
3. **关键任务**：使用 Qwen Max 或多模型投票
4. **多语言场景**：使用 Gemini
5. **超长文本**：使用 Gemini（支持百万 token）
6. **成本敏感**：使用 DeepSeek 或 Qwen Flash

---

更多示例请参考项目文档或联系开发团队。
