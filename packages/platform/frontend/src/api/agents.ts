/**
 * 代理相关 API
 */
import apiClient from './client'
import { Skill } from './skills'

export interface Agent {
  id: number
  name: string
  description?: string
  model_name: string
  temperature: number
  max_tokens?: number
  system_prompt?: string
  is_active: boolean
  created_by: number
  created_at: string
  updated_at: string
  skills: Skill[]
}

export interface AgentCreate {
  name: string
  description?: string
  model_name: string
  temperature?: number
  max_tokens?: number
  system_prompt?: string
  skill_ids?: number[]
}

export interface AgentUpdate {
  name?: string
  description?: string
  model_name?: string
  temperature?: number
  max_tokens?: number
  system_prompt?: string
  is_active?: boolean
  skill_ids?: number[]
}

export interface AgentExecuteRequest {
  message: string
}

export interface AgentExecuteResponse {
  execution_id: number
  status: string
  output_message?: string
  error_message?: string
  tokens_used?: number
  execution_time?: number
}

/**
 * 获取代理列表
 */
export const getAgents = async (params?: { is_active?: boolean; skip?: number; limit?: number }): Promise<Agent[]> => {
  const response = await apiClient.get<Agent[]>('/agents', { params })
  return response.data
}

/**
 * 获取单个代理详情
 */
export const getAgent = async (id: number): Promise<Agent> => {
  const response = await apiClient.get<Agent>(`/agents/${id}`)
  return response.data
}

/**
 * 创建代理
 */
export const createAgent = async (data: AgentCreate): Promise<Agent> => {
  const response = await apiClient.post<Agent>('/agents', data)
  return response.data
}

/**
 * 更新代理
 */
export const updateAgent = async (id: number, data: AgentUpdate): Promise<Agent> => {
  const response = await apiClient.put<Agent>(`/agents/${id}`, data)
  return response.data
}

/**
 * 删除代理
 */
export const deleteAgent = async (id: number): Promise<void> => {
  await apiClient.delete(`/agents/${id}`)
}

/**
 * 执行代理
 */
export const executeAgent = async (id: number, data: AgentExecuteRequest): Promise<AgentExecuteResponse> => {
  const response = await apiClient.post<AgentExecuteResponse>(`/agents/${id}/execute`, data)
  return response.data
}
