/**
 * 技能市场状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as marketplaceApi from '@/api/marketplace'
import type {
  MarketplaceSkill,
  MarketplaceListParams,
  TrySkillRequest,
  TrySkillResponse,
  CreateAgentFromSkillRequest,
  RateSkillRequest,
  SkillRating,
} from '@/api/marketplace'

export const useMarketplaceStore = defineStore('marketplace', () => {
  // 状态
  const skills = ref<MarketplaceSkill[]>([])
  const currentSkill = ref<MarketplaceSkill | null>(null)
  const savedSkills = ref<MarketplaceSkill[]>([])
  const loading = ref(false)
  const tryResult = ref<TrySkillResponse | null>(null)

  /**
   * 获取技能市场列表
   */
  const fetchMarketplaceSkills = async (params?: MarketplaceListParams) => {
    loading.value = true
    try {
      skills.value = await marketplaceApi.getMarketplaceSkills(params)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取技能市场详情
   */
  const fetchMarketplaceSkill = async (id: number) => {
    loading.value = true
    try {
      currentSkill.value = await marketplaceApi.getMarketplaceSkill(id)
    } finally {
      loading.value = false
    }
  }

  /**
   * 试用技能
   */
  const tryMarketplaceSkill = async (id: number, data: TrySkillRequest) => {
    loading.value = true
    try {
      tryResult.value = await marketplaceApi.trySkill(id, data)
      return tryResult.value
    } finally {
      loading.value = false
    }
  }

  /**
   * 从技能一键创建代理
   */
  const createAgentFromSkill = async (id: number, data: CreateAgentFromSkillRequest) => {
    loading.value = true
    try {
      const agent = await marketplaceApi.createAgentFromSkill(id, data)
      return agent
    } finally {
      loading.value = false
    }
  }

  /**
   * 收藏技能
   */
  const saveMarketplaceSkill = async (id: number) => {
    loading.value = true
    try {
      await marketplaceApi.saveSkill(id)
      // 更新列表中的收藏状态
      const skill = skills.value.find((s) => s.id === id)
      if (skill) {
        skill.is_saved = true
      }
      if (currentSkill.value?.id === id) {
        currentSkill.value.is_saved = true
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * 取消收藏技能
   */
  const unsaveMarketplaceSkill = async (id: number) => {
    loading.value = true
    try {
      await marketplaceApi.unsaveSkill(id)
      // 更新列表中的收藏状态
      const skill = skills.value.find((s) => s.id === id)
      if (skill) {
        skill.is_saved = false
      }
      if (currentSkill.value?.id === id) {
        currentSkill.value.is_saved = false
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * 评分技能
   */
  const rateMarketplaceSkill = async (id: number, data: RateSkillRequest) => {
    loading.value = true
    try {
      const rating = await marketplaceApi.rateSkill(id, data)
      // 更新列表中的评分信息
      const skill = skills.value.find((s) => s.id === id)
      if (skill) {
        skill.user_rating = data.rating
        // 重新获取列表以更新平均评分
        await fetchMarketplaceSkills()
      }
      if (currentSkill.value?.id === id) {
        currentSkill.value.user_rating = data.rating
        await fetchMarketplaceSkill(id)
      }
      return rating
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取我收藏的技能列表
   */
  const fetchSavedSkills = async (params?: { skip?: number; limit?: number }) => {
    loading.value = true
    try {
      savedSkills.value = await marketplaceApi.getMySavedSkills(params)
    } finally {
      loading.value = false
    }
  }

  /**
   * 清空当前技能
   */
  const clearCurrentSkill = () => {
    currentSkill.value = null
  }

  /**
   * 清空试用结果
   */
  const clearTryResult = () => {
    tryResult.value = null
  }

  return {
    skills,
    currentSkill,
    savedSkills,
    loading,
    tryResult,
    fetchMarketplaceSkills,
    fetchMarketplaceSkill,
    tryMarketplaceSkill,
    createAgentFromSkill,
    saveMarketplaceSkill,
    unsaveMarketplaceSkill,
    rateMarketplaceSkill,
    fetchSavedSkills,
    clearCurrentSkill,
    clearTryResult,
  }
})
