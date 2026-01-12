/**
 * 代理状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as agentsApi from '@/api/agents'
import type { Agent, AgentCreate, AgentUpdate, AgentExecuteRequest, AgentExecution } from '@/api/agents'

export const useAgentsStore = defineStore('agents', () => {
  // 状态
  const agents = ref<Agent[]>([])
  const currentAgent = ref<Agent | null>(null)
  const executions = ref<AgentExecution[]>([])
  const loading = ref(false)
  const executing = ref(false)

  /**
   * 获取代理列表
   */
  const fetchAgents = async (params?: { is_active?: boolean; skip?: number; limit?: number }) => {
    loading.value = true
    try {
      agents.value = await agentsApi.getAgents(params)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取单个代理详情
   */
  const fetchAgent = async (id: number) => {
    loading.value = true
    try {
      currentAgent.value = await agentsApi.getAgent(id)
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建代理
   */
  const createAgent = async (data: AgentCreate) => {
    loading.value = true
    try {
      const newAgent = await agentsApi.createAgent(data)
      agents.value.unshift(newAgent)
      return newAgent
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新代理
   */
  const updateAgent = async (id: number, data: AgentUpdate) => {
    loading.value = true
    try {
      const updatedAgent = await agentsApi.updateAgent(id, data)
      const index = agents.value.findIndex((a) => a.id === id)
      if (index !== -1) {
        agents.value[index] = updatedAgent
      }
      if (currentAgent.value?.id === id) {
        currentAgent.value = updatedAgent
      }
      return updatedAgent
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除代理
   */
  const deleteAgent = async (id: number) => {
    loading.value = true
    try {
      await agentsApi.deleteAgent(id)
      agents.value = agents.value.filter((a) => a.id !== id)
      if (currentAgent.value?.id === id) {
        currentAgent.value = null
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * 执行代理
   */
  const executeAgent = async (id: number, data: AgentExecuteRequest) => {
    executing.value = true
    try {
      const result = await agentsApi.executeAgent(id, data)
      return result
    } finally {
      executing.value = false
    }
  }

  /**
   * 清空当前代理
   */
  const clearCurrentAgent = () => {
    currentAgent.value = null
  }

  /**
   * 获取代理执行历史
   */
  const fetchExecutions = async (agentId: number, params?: { skip?: number; limit?: number; status?: string }) => {
    loading.value = true
    try {
      executions.value = await agentsApi.getAgentExecutions(agentId, params)
    } finally {
      loading.value = false
    }
  }

  return {
    agents,
    currentAgent,
    executions,
    loading,
    executing,
    fetchAgents,
    fetchAgent,
    createAgent,
    updateAgent,
    deleteAgent,
    executeAgent,
    clearCurrentAgent,
    fetchExecutions,
  }
})
