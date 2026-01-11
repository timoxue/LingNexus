/**
 * 监控相关 API
 */
import apiClient from './client'

export interface MonitoringProject {
  id: number
  name: string
  description?: string
  keywords: string[]
  companies?: string[]
  indications?: string[]
  is_active: boolean
  created_by: number
  created_at: string
  updated_at: string
  trial_count: number
}

export interface MonitoringProjectCreate {
  name: string
  description?: string
  keywords: string[]
  companies?: string[]
  indications?: string[]
}

export interface MonitoringProjectUpdate {
  description?: string
  keywords?: string[]
  companies?: string[]
  indications?: string[]
  is_active?: boolean
}

export interface ClinicalTrial {
  id: number
  project_id: number
  source: string
  nct_id?: string
  registration_number?: string
  title?: string
  status?: string
  phase?: string
  company?: string
  indication?: string
  start_date?: string
  completion_date?: string
  url?: string
  scraped_at: string
}

export interface ClinicalTrialListParams {
  project_id?: number
  source?: string
  status?: string
  limit?: number
  offset?: number
}

export interface MonitoringStatistics {
  projects: {
    total: number
    active: number
  }
  trials: {
    total: number
    by_source: Record<string, number>
    by_status: Record<string, number>
  }
}

/**
 * 获取监控项目列表
 */
export const getMonitoringProjects = async (params?: {
  is_active?: boolean
  skip?: number
  limit?: number
}): Promise<MonitoringProject[]> => {
  const response = await apiClient.get<MonitoringProject[]>('/monitoring/projects', { params })
  return response.data
}

/**
 * 获取单个监控项目详情
 */
export const getMonitoringProject = async (id: number): Promise<MonitoringProject> => {
  const response = await apiClient.get<MonitoringProject>(`/monitoring/projects/${id}`)
  return response.data
}

/**
 * 创建监控项目
 */
export const createMonitoringProject = async (data: MonitoringProjectCreate): Promise<MonitoringProject> => {
  const response = await apiClient.post<MonitoringProject>('/monitoring/projects', data)
  return response.data
}

/**
 * 更新监控项目
 */
export const updateMonitoringProject = async (
  id: number,
  data: MonitoringProjectUpdate
): Promise<MonitoringProject> => {
  const response = await apiClient.put<MonitoringProject>(`/monitoring/projects/${id}`, data)
  return response.data
}

/**
 * 删除监控项目
 */
export const deleteMonitoringProject = async (id: number): Promise<void> => {
  await apiClient.delete(`/monitoring/projects/${id}`)
}

/**
 * 获取临床试验列表
 */
export const getClinicalTrials = async (params?: ClinicalTrialListParams): Promise<ClinicalTrial[]> => {
  const response = await apiClient.get<ClinicalTrial[]>('/monitoring/trials', { params })
  return response.data
}

/**
 * 获取单个临床试验详情
 */
export const getClinicalTrial = async (id: number): Promise<ClinicalTrial> => {
  const response = await apiClient.get<ClinicalTrial>(`/monitoring/trials/${id}`)
  return response.data
}

/**
 * 获取监控统计信息
 */
export const getMonitoringStatistics = async (): Promise<MonitoringStatistics> => {
  const response = await apiClient.get<MonitoringStatistics>('/monitoring/statistics')
  return response.data
}
