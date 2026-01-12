/**
 * 通用类型定义
 */

/**
 * API响应基础类型
 */
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: {
    code: string
    message: string
    details?: any
  }
  timestamp?: string
}

/**
 * 分页参数
 */
export interface PaginationParams {
  page?: number
  pageSize?: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

/**
 * 分页响应
 */
export interface PaginationResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

/**
 * 用户相关类型
 */
export interface User {
  id: number
  username: string
  email: string
  fullName?: string
  department?: string
  role: 'user' | 'admin' | 'super_admin'
  xp: number
  level: number
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token?: string
  expires_in: number
  user: User
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
  department?: string
}

/**
 * 技能相关类型
 */
export interface Skill {
  id: number
  name: string
  category: 'external' | 'internal'
  content: string
  meta?: Record<string, any>
  isActive: boolean
  version: string
  createdBy: number
  creator?: User
  sharingScope: 'private' | 'team' | 'public'
  department?: string
  isOfficial: boolean
  usageCount: number
  rating?: number
  ratingCount: number
  documentation?: string
  createdAt: string
  updatedAt: string
}

export interface CreateSkillRequest {
  name: string
  category: 'external' | 'internal'
  content: string
  meta?: Record<string, any>
  sharingScope?: 'private' | 'team' | 'public'
  documentation?: string
}

export interface UpdateSkillRequest {
  name?: string
  content?: string
  meta?: Record<string, any>
  sharingScope?: 'private' | 'team' | 'public'
  documentation?: string
}

/**
 * Agent相关类型
 */
export interface Agent {
  id: number
  name: string
  description?: string
  modelName: string
  modelType: 'qwen' | 'deepseek'
  temperature: number
  maxTokens: number
  systemPrompt?: string
  config: Record<string, any>
  createdBy: number
  creator?: User
  skills: Skill[]
  createdAt: string
  updatedAt: string
}

export interface CreateAgentRequest {
  name: string
  description?: string
  modelName: string
  temperature: number
  maxTokens?: number
  systemPrompt?: string
  skillIds?: number[]
  config?: Record<string, any>
}

export interface AgentExecutionRequest {
  message: string
  stream?: boolean
}

export interface AgentExecutionResponse {
  executionId: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  output?: string
  errorMessage?: string
  tokensUsed?: number
  executionTime?: number
  createdAt: string
  completedAt?: string
}

/**
 * 市场相关类型
 */
export interface MarketplaceSkill extends Skill {
  isFavorited?: boolean
  userRating?: number
}

export interface TrySkillRequest {
  message: string
}

export interface TrySkillResponse {
  output: string
  tokensUsed?: number
  executionTime?: number
}

export interface SkillRatingRequest {
  rating: number
  comment?: string
}

/**
 * 监控相关类型
 */
export interface MonitoringProject {
  id: number
  name: string
  englishName: string
  category: string
  type: string
  keywords: string[]
  companies: string[]
  createdBy: number
  createdAt: string
}

export interface ClinicalTrial {
  id: number
  nctId: string
  title: string
  status?: string
  phase?: string
  startDate?: string
  primaryCompletionDate?: string
  conditions?: string
  interventions?: string
  source: 'ClinicalTrials.gov' | 'CDE'
  url?: string
  collectedAt: string
}

/**
 * 路由相关类型
 */
export type RouteRecordRaw = import('vue-router').RouteRecordRaw

export interface MenuItem {
  path: string
  name: string
  title: string
  icon?: any
  children?: MenuItem[]
  meta?: {
    requiresAuth?: boolean
    roles?: string[]
    hidden?: boolean
  }
}
