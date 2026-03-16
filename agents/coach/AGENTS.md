# AGENTS CONFIG: coach

## agent_id
coach

## version
1.0.0

## role
strategist

## capabilities
- read_shared_memory
- write_shared_memory
- decompose_query

## tools
[]

## trigger
- workflow: biopharma-scouting
- step: 1 (first in pipeline)
- input_from: main (payload.raw_query)

## on_activate
1. Read `raw_query` from workflow payload
2. Analyze query intent (therapeutic area, target, geography, time range)
3. Decompose into exactly 5 search sub-tasks following the 5-Track Protocol in SOUL.md
4. Validate all 5 tasks are generated before writing to blackboard
5. Write task array to shared blackboard: [Pending_Tasks]
6. Mark self as complete, signal `investigator` to start

## blackboard_write_format
Target: [Pending_Tasks]
```json
[
  {
    "task_id": "T1",
    "language": "en",
    "region": "GLOBAL",
    "target_source": "PubMed + Google Patents + USPTO",
    "search_query": "{english_boolean_query}",
    "priority": 1,
    "status": "pending"
  },
  {
    "task_id": "T2",
    "language": "zh",
    "region": "CN",
    "target_source": "药智网 + CNIPA + CDE",
    "search_query": "{chinese_query}",
    "priority": 2,
    "status": "pending"
  },
  {
    "task_id": "T3",
    "language": "ja",
    "region": "JP",
    "target_source": "JMACCT + J-PlatPat",
    "search_query": "{japanese_query}",
    "priority": 3,
    "status": "pending"
  },
  {
    "task_id": "T4",
    "language": "en|ko",
    "region": "EU|KR",
    "target_source": "Espacenet + KIPRISPlus",
    "search_query": "{english_korean_query}",
    "priority": 4,
    "status": "pending"
  },
  {
    "task_id": "T5",
    "language": "en|zh",
    "region": "GLOBAL",
    "target_source": "Fierce Pharma + BioCentury + 医药魔方",
    "search_query": "{mixed_query}",
    "priority": 5,
    "status": "pending"
  }
]
```

## shared_memory_access
- read: []
- write: ["Pending_Tasks"]

## next_agents
- investigator
