# AGENTS CONFIG: deduplicator

## agent_id
deduplicator

## version
1.0.0

## role
output_formatter

## capabilities
- read_shared_memory
- write_shared_memory
- cross_lingual_entity_disambiguation
- markdown_generation

## tools
[]

## trigger
- workflow: biopharma-scouting
- step: 4 (final step)
- input_from: validator (blackboard [Validated_Assets])

## on_activate
1. Read ALL objects from [Validated_Assets] where `is_met: true`
2. Execute cross-lingual entity disambiguation (see dedup_logic below)
3. Build merged entity registry
4. Render Markdown report following SOUL.md template
5. Write final Markdown to workflow output: `deduplicator.output`
6. Signal workflow completion to `main`

## dedup_logic
```
Phase 1 - Normalization:
  For each drug_candidate string:
    - Strip special chars, hyphens, spaces → normalize form
    - Map Chinese drug names to English INN/brand equivalents
    - Map Japanese katakana drug names to English equivalents
    - Build alias_set: {ARV-471, ARV471, 阿维替尼, アルビ}

Phase 2 - Clustering:
  Group entries by: normalized(drug_candidate) + normalized(entity_name)
  Primary key: (canonical_drug_name, canonical_entity_name)

Phase 3 - Merging:
  For each cluster:
    - canonical_drug_name: English INN or most-cited name
    - aliases: all non-canonical names from cluster
    - origin_country: union of all unique country codes
    - evidence_quote: select most authoritative quote (USPTO/CNIPA patent > news)
    - clinical_stage: take most advanced stage across cluster
    - validated_at: take most recent timestamp

Phase 4 - Sorting:
  Sort final entries by: priority(degrader_modality) DESC, clinical_stage DESC
```

## shared_memory_access
- read: ["Validated_Assets"]
- write: []  # output goes directly to workflow return payload

## workflow_output
- key: deduplicator.output
- type: markdown_string
- consumer: main (pushes to feishu user)

## next_agents
[]  # terminal node
