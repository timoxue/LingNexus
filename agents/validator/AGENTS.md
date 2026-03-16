# AGENTS CONFIG: validator

## agent_id
validator

## version
1.0.0

## role
quality_control

## capabilities
- read_shared_memory
- write_shared_memory

## tools
[]  # PHYSICALLY DISCONNECTED - no web access, no external APIs

## trigger
- workflow: biopharma-scouting
- step: 3
- input_from: investigator (blackboard [Raw_Evidence])

## on_activate
1. Read ALL evidence objects with `status: "pending_validation"` from [Raw_Evidence]
2. For each evidence object, apply ALL 4 hard interception rules (AND logic — all must pass):
   - Rule 1 (TIME): Extract date from raw_text → must fall in [2023-01-01, 2026-12-31]
   - Rule 2 (MODALITY): raw_text must explicitly mention a targeted degrader modality
   - Rule 3 (STAGE): raw_text must explicitly indicate early clinical stage
   - Rule 4 (ENTITY_COUNTRY): Extract origin_country from company/institution mentions
3. If ALL rules pass → `is_met: true` → write to [Validated_Assets]
4. If ANY rule fails → `is_met: false` → write to [Rejected_Evidence] with failure_rationale

## validation_rules_detail
```
Rule 1 - TIME RANGE:
  Keywords: date, filed, published, registered, 申请日, 公开日, 登记日, 出願日
  Range: 2023-01-01 to 2026-12-31
  Fail: "Date {extracted_date} outside 2023-2026 window"

Rule 2 - DEGRADER MODALITY:
  Accept: PROTAC, Molecular Glue, LYTAC, ATTEC, AUTAC, targeted protein degradation,
          蛋白降解, 分子胶, ターゲットタンパク質分解, 표적 단백질 분해
  Fail: "No targeted degrader modality keyword found in raw_text"

Rule 3 - CLINICAL STAGE:
  Accept: Pre-Clinical, Preclinical, IND, Phase 1, Phase I, Phase 1/2, Phase I/II,
          临床前, IND申请, 一期临床, 前臨床, 第I相
  Fail: "Clinical stage {extracted_stage} is Phase II or later"

Rule 4 - ORIGIN COUNTRY:
  Extract from: company address, HQ mention, patent assignee country code,
                国家, 总部, 所在地, 国籍
  Normalize to ISO 3166-1 alpha-2 (CN, US, JP, DE, KR, GB, FR, etc.)
  Fail: "Cannot determine origin_country from raw_text — set to null"
```

## output_write_format
Target: [Validated_Assets] (is_met: true only)
Target: [Rejected_Evidence] (is_met: false)

## shared_memory_access
- read: ["Raw_Evidence"]
- write: ["Validated_Assets", "Rejected_Evidence"]

## next_agents
- deduplicator
