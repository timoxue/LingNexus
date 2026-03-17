# AGENTS CONFIG: investigator

## agent_id
investigator

## version
1.0.0

## role
crawler

## capabilities
- read_shared_memory
- write_shared_memory
- web_search
- language_parallelism

## tools
- global_intelligence_search:
    type: custom_skill
    path: skills/global_search_skill.py
    max_concurrent: 5
    supported_languages: [zh, en, ja, ko, de]
    timeout_per_task: 60s
    allowed_domains: [pubmed, general_web]
- web_search:
    max_concurrent: 5
    supported_languages: [zh, en, ja, ko, de]
    timeout_per_task: 60s

## subagents
- investigator:
    allowAgents: ["investigator"]
    maxConcurrent: 5
    timeoutSeconds: 60
    cleanup: delete

## trigger
- workflow: biopharma-scouting
- step: 2
- input_from: coach (blackboard [Pending_Tasks])

## on_activate
1. Read all tasks with `status: "pending"` from [Pending_Tasks]
2. Execute ALL tasks concurrently (do NOT wait sequentially)
3. For each task:
   a. Execute web_search using task.search_query in task.language against task.target_source
   b. Collect raw text results — NO summarization, NO filtering
   c. Update task status to "completed" in [Pending_Tasks]
   d. Write evidence object to [Raw_Evidence]
4. After all 5 tasks complete, signal `validator` to start

## parallelism_model
```
Task T1 ──┐
Task T2 ──┤
Task T3 ──┼──► concurrent execution ──► write to [Raw_Evidence]
Task T4 ──┤
Task T5 ──┘
```

## evidence_write_format
Target: [Raw_Evidence]
Each search result becomes one evidence object:
```json
{
  "evidence_id": "E{unix_timestamp}_{task_id}_{result_index}",
  "source_task_id": "T{n}",
  "language": "{task.language}",
  "region": "{task.region}",
  "source_url": "{result.url}",
  "source_name": "{task.target_source}",
  "raw_text": "{full unmodified result text}",
  "crawled_at": "{ISO8601}",
  "status": "pending_validation"
}
```

## strict_no_llm_rule
- raw_text MUST be verbatim crawled text
- No summarization
- No inference
- No filtering by relevance

## shared_memory_access
- read: ["Pending_Tasks"]
- write: ["Raw_Evidence", "Pending_Tasks"]

## next_agents
- validator
