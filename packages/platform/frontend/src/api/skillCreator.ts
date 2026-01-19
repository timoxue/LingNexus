/**
 * Skill Creator API Client
 *
 * 与后端 Skill Creator Agent API 交互
 * 集成 AgentScope ReActAgent 对话系统
 */

import client from './client'

// ========== 类型定义 ==========

interface CreateSessionRequest {
  use_api_key: boolean
}

interface CreateSessionResponse {
  session_id: string
  type: string
  current_dimension: string
  dimension_name: string
  question: string
  guidance: string
  placeholder: string
  examples: string[]
  progress: {
    current: number
    total: number
    percentage: number
  }
}

interface ChatRequest {
  session_id: string
  message: string
}

interface ChatResponse {
  type: 'next_dimension' | 'follow_up' | 'summary' | 'error'
  current_dimension?: string
  dimension_name?: string
  question?: string
  guidance?: string
  follow_up_question?: string
  score?: number
  reasoning?: string
  recommended_options?: Array<{
    id: string
    text: string
  }>
  examples?: string[]
  progress?: {
    current: number
    total: number
    percentage: number
  }
  skill_metadata?: {
    skill_name: string
    core_value: string
    usage_scenario: string
    main_alias: string
    context_aliases: string[]
    description: string
    category: string
    degrees_of_freedom: string
    suggested_resources: {
      scripts: string[]
      references: string[]
      assets: string[]
    }
  }
  message?: string
  next_step?: string
}

interface SessionStatus {
  session_id: string
  current_dimension_idx: number
  current_dimension: string
  created_at: string
  last_activity: string
  is_expired: boolean
}

interface SaveSkillResponse {
  skill_id: number
  skill_name: string
  message: string
}

// ========== Agent 对话 API ==========

/**
 * 创建 Agent 会话 - 开始渐进式技能定义
 */
export async function createAgentSession(useApiKey = false): Promise<CreateSessionResponse> {
  const response = await client.post<CreateSessionResponse>(
    '/skill-creator-agent/session/create',
    { use_api_key: useApiKey }
  )
  return response.data
}

/**
 * 与 Agent 对话 - 回答问题或补充信息
 */
export async function agentChat(sessionId: string, message: string): Promise<ChatResponse> {
  const response = await client.post<ChatResponse>('/skill-creator-agent/chat', {
    session_id: sessionId,
    message,
  })
  return response.data
}

/**
 * 结束 Agent 会话 - 生成最终技能元数据
 */
export async function endAgentSession(sessionId: string): Promise<ChatResponse> {
  const response = await client.post<ChatResponse>(
    `/skill-creator-agent/session/end?session_id=${sessionId}`,
    {}
  )
  return response.data
}

/**
 * 获取会话状态
 */
export async function getSessionStatus(sessionId: string): Promise<SessionStatus> {
  const response = await client.get<SessionStatus>(`/skill-creator-agent/session/${sessionId}`)
  return response.data
}

/**
 * 从会话保存技能到数据库
 */
export async function saveSkillFromSession(sessionId: string): Promise<SaveSkillResponse> {
  const response = await client.post<SaveSkillResponse>(
    `/skill-creator-agent/session/${sessionId}/save-skill`,
    {}
  )
  return response.data
}

// ========== 导出 API 对象 ==========

export const skillCreatorApi = {
  createAgentSession,
  agentChat,
  endAgentSession,
  getSessionStatus,
  saveSkillFromSession,
}
