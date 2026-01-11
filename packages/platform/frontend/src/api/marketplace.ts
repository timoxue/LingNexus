/**
 * 技能市场相关 API
 */
import apiClient from './client'

// ==================== 类型定义 ====================

export interface MarketplaceSkill {
  id: number
  name: string
  category: 'external' | 'internal'
  content: string
  meta?: Record<string, any>
  is_active: boolean
  version: string
  created_by: number
  created_at: string
  updated_at: string
  sharing_scope: 'private' | 'team' | 'public'
  department?: string
  is_official: boolean
  usage_count: number
  rating: number | null
  rating_count: number
  documentation?: string
  creator_name?: string
  is_saved: boolean
  user_rating?: number
}

export interface MarketplaceListParams {
  category?: 'external' | 'internal'
  sharing_scope?: 'private' | 'team' | 'public'
  search?: string
  sort_by?: 'created_at' | 'rating' | 'usage_count'
  department?: string
  is_official?: boolean
  skip?: number
  limit?: number
}

export interface TrySkillRequest {
  message: string
}

export interface TrySkillResponse {
  status: string
  output_message?: string
  error_message?: string
  execution_time?: number
}

export interface CreateAgentFromSkillRequest {
  agent_name: string
  description?: string
  model_name?: string
  temperature?: number
  max_tokens?: number
}

export interface RateSkillRequest {
  rating: number
  comment?: string
}

export interface SkillRating {
  id: number
  user_id: number
  skill_id: number
  rating: number
  comment?: string
  created_at: string
}

// ==================== API 函数 ====================

/**
 * 获取技能市场列表
 */
export const getMarketplaceSkills = async (params?: MarketplaceListParams): Promise<MarketplaceSkill[]> => {
  const response = await apiClient.get<MarketplaceSkill[]>('/marketplace/skills', { params })
  return response.data
}

/**
 * 获取技能市场详情
 */
export const getMarketplaceSkill = async (id: number): Promise<MarketplaceSkill> => {
  const response = await apiClient.get<MarketplaceSkill>(`/marketplace/skills/${id}`)
  return response.data
}

/**
 * 试用技能（无需登录）
 */
export const trySkill = async (id: number, data: TrySkillRequest): Promise<TrySkillResponse> => {
  const response = await apiClient.post<TrySkillResponse>(`/marketplace/skills/${id}/try`, data)
  return response.data
}

/**
 * 从技能一键创建代理
 */
export const createAgentFromSkill = async (
  id: number,
  data: CreateAgentFromSkillRequest
): Promise<any> => {
  const response = await apiClient.post(`/marketplace/skills/${id}/create-agent`, data)
  return response.data
}

/**
 * 收藏技能
 */
export const saveSkill = async (id: number): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>(`/marketplace/skills/${id}/save`)
  return response.data
}

/**
 * 取消收藏技能
 */
export const unsaveSkill = async (id: number): Promise<void> => {
  await apiClient.delete(`/marketplace/skills/${id}/save`)
}

/**
 * 评分技能
 */
export const rateSkill = async (id: number, data: RateSkillRequest): Promise<SkillRating> => {
  const response = await apiClient.post<SkillRating>(`/marketplace/skills/${id}/rate`, data)
  return response.data
}

/**
 * 获取我收藏的技能列表
 */
export const getMySavedSkills = async (params?: { skip?: number; limit?: number }): Promise<MarketplaceSkill[]> => {
  const response = await apiClient.get<MarketplaceSkill[]>('/marketplace/my/saved', { params })
  return response.data
}
