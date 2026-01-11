/**
 * 技能相关 API
 */
import apiClient from './client'

export interface Skill {
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
}

export interface SkillCreate {
  name: string
  category: 'external' | 'internal'
  content: string
  meta?: Record<string, any>
}

export interface SkillUpdate {
  content?: string
  meta?: Record<string, any>
  is_active?: boolean
}

export interface SkillListParams {
  category?: 'external' | 'internal'
  is_active?: boolean
  skip?: number
  limit?: number
}

/**
 * 获取技能列表
 */
export const getSkills = async (params?: SkillListParams): Promise<Skill[]> => {
  const response = await apiClient.get<Skill[]>('/skills', { params })
  return response.data
}

/**
 * 获取单个技能详情
 */
export const getSkill = async (id: number): Promise<Skill> => {
  const response = await apiClient.get<Skill>(`/skills/${id}`)
  return response.data
}

/**
 * 创建技能
 */
export const createSkill = async (data: SkillCreate): Promise<Skill> => {
  const response = await apiClient.post<Skill>('/skills', data)
  return response.data
}

/**
 * 更新技能
 */
export const updateSkill = async (id: number, data: SkillUpdate): Promise<Skill> => {
  const response = await apiClient.put<Skill>(`/skills/${id}`, data)
  return response.data
}

/**
 * 删除技能
 */
export const deleteSkill = async (id: number): Promise<void> => {
  await apiClient.delete(`/skills/${id}`)
}
