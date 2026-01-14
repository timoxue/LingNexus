/**
 * 文件管理 API
 */
import apiClient from './client'

/**
 * Agent 生成的文件
 */
export interface AgentArtifact {
  id: number
  file_id: string
  agent_execution_id: number
  skill_id?: number
  filename: string
  original_filename?: string
  file_type: string
  file_size: number
  mime_type: string
  category: string
  description?: string
  storage_path: string
  access_count: number
  last_accessed_at?: string
  created_at: string
  download_url: string
  preview_url: string
}

/**
 * 用户文件
 */
export interface UserFile {
  id: number
  file_id: string
  user_id: number
  folder_id?: number
  filename: string
  file_type: string
  file_size: number
  mime_type: string
  storage_path: string
  description?: string
  tags?: string
  access_count: number
  last_accessed_at?: string
  created_at: string
  updated_at: string
  download_url: string
  preview_url: string
}

/**
 * 用户文件夹
 */
export interface UserFolder {
  id: number
  user_id: number
  parent_id?: number
  name: string
  description?: string
  path: string
  order: number
  created_at: string
  updated_at: string
  file_count: number
  folder_count: number
}

/**
 * 文件上传响应
 */
export interface FileUploadResponse {
  file_id: string
  filename: string
  file_type: string
  file_size: number
  storage_path: string
  download_url: string
  preview_url: string
}

// ==================== Agent Artifacts ====================

/**
 * 获取 Agent 生成的文件列表
 */
export const getAgentArtifacts = async (params?: {
  agent_execution_id?: number
  skill_id?: number
  skip?: number
  limit?: number
}): Promise<AgentArtifact[]> => {
  const response = await apiClient.get<AgentArtifact[]>('/files/artifacts', { params })
  return response.data
}

/**
 * 下载 Agent 生成的文件
 */
export const downloadAgentArtifact = async (fileId: string): Promise<Blob> => {
  const response = await apiClient.get(`/files/artifacts/${fileId}/download`, {
    responseType: 'blob',
  })
  return response.data
}

/**
 * 获取文件下载 URL（用于 <a> 标签或 iframe）
 */
export const getAgentArtifactDownloadUrl = (fileId: string): string => {
  return `/api/v1/files/artifacts/${fileId}/download`
}

/**
 * 获取文件预览 URL（用于 iframe 或 img 标签）
 */
export const getAgentArtifactPreviewUrl = (fileId: string): string => {
  return `/api/v1/files/artifacts/${fileId}/preview`
}

// ==================== User Files ====================

/**
 * 上传文件
 */
export const uploadFile = async (
  file: File,
  folderId?: number,
  description?: string
): Promise<UserFile> => {
  const formData = new FormData()
  formData.append('file', file)
  if (folderId) formData.append('folder_id', folderId.toString())
  if (description) formData.append('description', description)

  const response = await apiClient.post<UserFile>('/files/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

/**
 * 获取文件列表
 */
export const getFiles = async (params?: {
  folder_id?: number
  skip?: number
  limit?: number
  search?: string
}): Promise<UserFile[]> => {
  const response = await apiClient.get<UserFile[]>('/files', { params })
  return response.data
}

/**
 * 下载文件
 */
export const downloadFile = async (fileId: string): Promise<Blob> => {
  const response = await apiClient.get(`/files/${fileId}/download`, {
    responseType: 'blob',
  })
  return response.data
}

/**
 * 预览文件
 */
export const previewFile = async (fileId: string): Promise<Blob> => {
  const response = await apiClient.get(`/files/${fileId}/preview`, {
    responseType: 'blob',
  })
  return response.data
}

/**
 * 删除文件
 */
export const deleteFile = async (fileId: string): Promise<{ message: string }> => {
  const response = await apiClient.delete(`/files/${fileId}`)
  return response.data
}

/**
 * 移动文件
 */
export const moveFile = async (
  fileId: string,
  targetFolderId?: number
): Promise<UserFile> => {
  const response = await apiClient.put(`/files/${fileId}/move`, null, {
    params: { target_folder_id: targetFolderId },
  })
  return response.data
}

// ==================== User Folders ====================

/**
 * 创建文件夹
 */
export const createFolder = async (data: {
  name: string
  description?: string
  parent_id?: number
}): Promise<UserFolder> => {
  const formData = new FormData()
  formData.append('name', data.name)
  if (data.description) formData.append('description', data.description)
  if (data.parent_id) formData.append('parent_id', data.parent_id.toString())

  const response = await apiClient.post<UserFolder>('/files/folders', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

/**
 * 获取文件夹列表
 */
export const getFolders = async (params?: {
  parent_id?: number
}): Promise<UserFolder[]> => {
  const response = await apiClient.get<UserFolder[]>('/files/folders', { params })
  return response.data
}

/**
 * 更新文件夹
 */
export const updateFolder = async (
  folderId: number,
  data: {
    name?: string
    description?: string
    parent_id?: number
    order?: number
  }
): Promise<UserFolder> => {
  const response = await apiClient.put<UserFolder>(`/files/folders/${folderId}`, data)
  return response.data
}

/**
 * 删除文件夹
 */
export const deleteFolder = async (folderId: number): Promise<{ message: string }> => {
  const response = await apiClient.delete(`/files/folders/${folderId}`)
  return response.data
}
