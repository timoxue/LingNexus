/**
 * 技能状态管理（优化版）
 */
import { defineStore } from 'pinia'
import { computed } from 'vue'
import * as skillsApi from '@/api/skills'
import type { Skill, SkillListParams, SkillCreate, SkillUpdate } from '@/api/skills'
import { useBaseStore, createCacheKey } from '@/composables/useBaseStore'

export const useSkillsStore = defineStore('skills', () => {
  // Use base store for common functionality
  const baseStore = useBaseStore<Skill>('skills')

  // Computed properties for backward compatibility
  const skills = computed(() => baseStore.items.value)
  const currentSkill = computed(() => baseStore.currentItem.value)
  const loading = computed(() => baseStore.loading.value)
  const error = computed(() => baseStore.error.value)
  const total = computed(() => baseStore.pagination.value.total)

  /**
   * 获取技能列表（带缓存和去重）
   */
  const fetchSkills = async (params?: SkillListParams) => {
    const cacheKey = createCacheKey('skills', 'list', params)

    return baseStore.executeAsync(async () => {
      const result = await baseStore.deduplicateRequest(cacheKey, async () => {
        return await skillsApi.getSkills(params)
      })

      // Handle pagination if returned
      if (Array.isArray(result)) {
        baseStore.updateItems(result)
        baseStore.updatePagination({ total: result.length })
      } else if (result?.items) {
        baseStore.updateItems(result.items)
        baseStore.updatePagination({
          page: result.page || 1,
          pageSize: result.pageSize || 20,
          total: result.total || 0
        })
      }

      return result
    })
  }

  /**
   * 获取单个技能详情（带缓存）
   */
  const fetchSkill = async (id: number) => {
    const cacheKey = createCacheKey('skills', 'detail', id)

    return baseStore.executeAsync(async () => {
      const result = await baseStore.deduplicateRequest(cacheKey, async () => {
        return await skillsApi.getSkill(id)
      })

      baseStore.setCurrentItem(result)
      return result
    })
  }

  /**
   * 创建技能（带乐观更新）
   */
  const createSkill = async (data: SkillCreate, options = { optimistic: true }) => {
    const tempId = `temp-${Date.now()}`

    if (options.optimistic) {
      baseStore.optimisticUpdate(tempId, data as Partial<Skill>, tempId)
    }

    return baseStore.executeAsync(async () => {
      const newSkill = await skillsApi.createSkill(data)

      if (options.optimistic) {
        baseStore.revertOptimisticUpdate(tempId, tempId)
      }

      baseStore.addItem(newSkill)
      return newSkill
    }, { silent: options.optimistic }).catch((err) => {
      if (options.optimistic) {
        baseStore.revertOptimisticUpdate(tempId, tempId)
      }
      throw err
    })
  }

  /**
   * 更新技能（带乐观更新）
   */
  const updateSkill = async (id: number, data: SkillUpdate, options = { optimistic: true }) => {
    // Store previous state for rollback
    const previousItem = skills.value.find((s) => s.id === id)

    if (options.optimistic && previousItem) {
      baseStore.updateItem(id, data)
    }

    return baseStore.executeAsync(async () => {
      const updatedSkill = await skillsApi.updateSkill(id, data)
      baseStore.updateItem(id, updatedSkill)
      return updatedSkill
    }, { silent: options.optimistic }).catch((err) => {
      if (options.optimistic && previousItem) {
        baseStore.updateItem(id, previousItem)
      }
      throw err
    })
  }

  /**
   * 删除技能（带乐观更新）
   */
  const deleteSkill = async (id: number, options = { optimistic: true }) => {
    // Store previous state for rollback
    const previousItem = skills.value.find((s) => s.id === id)
    const previousCurrent = currentSkill.value

    if (options.optimistic) {
      baseStore.removeItem(id)
    }

    return baseStore.executeAsync(async () => {
      await skillsApi.deleteSkill(id)
    }, { silent: options.optimistic }).catch((err) => {
      if (options.optimistic) {
        if (previousItem) {
          baseStore.addItem(previousItem)
        }
        if (previousCurrent?.id === id) {
          baseStore.setCurrentItem(previousCurrent)
        }
      }
      throw err
    })
  }

  /**
   * 清空当前技能
   */
  const clearCurrentSkill = () => {
    baseStore.setCurrentItem(null)
  }

  /**
   * 重置所有状态
   */
  const reset = () => {
    baseStore.reset()
  }

  return {
    // State
    skills,
    currentSkill,
    loading,
    error,
    total,

    // Actions
    fetchSkills,
    fetchSkill,
    createSkill,
    updateSkill,
    deleteSkill,
    clearCurrentSkill,
    reset
  }
})
