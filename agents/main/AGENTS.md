# AGENTS CONFIG: main

## agent_id
main

## version
1.0.0

## role
gateway

## channel_bindings
- channel: feishu
  trigger_keywords: ["专利", "挖掘", "靶向药", "全球"]
  match_mode: any_of

## capabilities
- receive_user_message
- send_user_message
- trigger_workflow

## tools
[
  {
    "name": "send_message",
    "description": "Send a message to another agent via ACP (Agent Control Protocol)",
    "parameters": {
      "type": "object",
      "properties": {
        "agent": {
          "type": "string",
          "description": "Target agent ID (e.g., 'coach', 'investigator')"
        },
        "message": {
          "type": "string",
          "description": "Message content to send to the agent"
        }
      },
      "required": ["agent", "message"]
    }
  }
]

## on_message
1. Extract `user_query` from incoming message
2. Reply with acknowledgement using tone template from SOUL.md
3. Call workflow: `biopharma-scouting`
   - payload: { "raw_query": "{user_query}", "channel": "feishu", "user_id": "{user_id}" }
4. Poll workflow status every 30s, send progress update to user
5. On workflow completion, retrieve `deduplicator.output` and push to user verbatim

## error_handling
- On workflow timeout (>10min): notify user with apology, log error to system
- On workflow failure: return structured error message, suggest retry

## shared_memory_access
- read: []
- write: []

## next_agents
[]  # main is terminal; workflow handles sequencing
