/**
 * 监控状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as monitoringApi from '@/api/monitoring'
import type {
  MonitoringProject,
  MonitoringProjectCreate,
  MonitoringProjectUpdate,
  ClinicalTrial,
  ClinicalTrialListParams,
  MonitoringStatistics,
} from '@/api/monitoring'

export const useMonitoringStore = defineStore('monitoring', () => {
  // 状态
  const projects = ref<MonitoringProject[]>([])
  const currentProject = ref<MonitoringProject | null>(null)
  const trials = ref<ClinicalTrial[]>([])
  const statistics = ref<MonitoringStatistics | null>(null)
  const loading = ref(false)

  /**
   * 获取监控项目列表
   */
  const fetchProjects = async (params?: { is_active?: boolean; skip?: number; limit?: number }) => {
    loading.value = true
    try {
      projects.value = await monitoringApi.getMonitoringProjects(params)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取单个监控项目详情
   */
  const fetchProject = async (id: number) => {
    loading.value = true
    try {
      currentProject.value = await monitoringApi.getMonitoringProject(id)
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建监控项目
   */
  const createProject = async (data: MonitoringProjectCreate) => {
    loading.value = true
    try {
      const newProject = await monitoringApi.createMonitoringProject(data)
      projects.value.unshift(newProject)
      return newProject
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新监控项目
   */
  const updateProject = async (id: number, data: MonitoringProjectUpdate) => {
    loading.value = true
    try {
      const updatedProject = await monitoringApi.updateMonitoringProject(id, data)
      const index = projects.value.findIndex((p) => p.id === id)
      if (index !== -1) {
        projects.value[index] = updatedProject
      }
      if (currentProject.value?.id === id) {
        currentProject.value = updatedProject
      }
      return updatedProject
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除监控项目
   */
  const deleteProject = async (id: number) => {
    loading.value = true
    try {
      await monitoringApi.deleteMonitoringProject(id)
      projects.value = projects.value.filter((p) => p.id !== id)
      if (currentProject.value?.id === id) {
        currentProject.value = null
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取临床试验列表
   */
  const fetchTrials = async (params?: ClinicalTrialListParams) => {
    loading.value = true
    try {
      trials.value = await monitoringApi.getClinicalTrials(params)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取监控统计信息
   */
  const fetchStatistics = async () => {
    loading.value = true
    try {
      statistics.value = await monitoringApi.getMonitoringStatistics()
    } finally {
      loading.value = false
    }
  }

  /**
   * 清空当前项目
   */
  const clearCurrentProject = () => {
    currentProject.value = null
  }

  return {
    projects,
    currentProject,
    trials,
    statistics,
    loading,
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject,
    fetchTrials,
    fetchStatistics,
    clearCurrentProject,
  }
})
