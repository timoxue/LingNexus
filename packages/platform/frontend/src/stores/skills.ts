/**
 * 技能状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as skillsApi from '@/api/skills'
import type { Skill, SkillListParams, SkillCreate, SkillUpdate } from '@/api/skills'

export const useSkillsStore = defineStore('skills', () => {
  // 状态
  const skills = ref<Skill[]>([])
  const currentSkill = ref<Skill | null>(null)
  const loading = ref(false)
  const total = ref(0)

  /**
   * 获取技能列表
   */
  const fetchSkills = async (params?: SkillListParams) => {
    loading.value = true
    try {
      skills.value = await skillsApi.getSkills(params)
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取单个技能详情
   */
  const fetchSkill = async (id: number) => {
    loading.value = true
    try {
      currentSkill.value = await skillsApi.getSkill(id)
    } finally {
      loading.value = false
    }
  }

  /**
   * 创建技能
   */
  const createSkill = async (data: SkillCreate) => {
    loading.value = true
    try {
      const newSkill = await skillsApi.createSkill(data)
      skills.value.unshift(newSkill)
      return newSkill
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新技能
   */
  const updateSkill = async (id: number, data: SkillUpdate) => {
    loading.value = true
    try {
      const updatedSkill = await skillsApi.updateSkill(id, data)
      const index = skills.value.findIndex((s) => s.id === id)
      if (index !== -1) {
        skills.value[index] = updatedSkill
      }
      if (currentSkill.value?.id === id) {
        currentSkill.value = updatedSkill
      }
      return updatedSkill
    } finally {
      loading.value = false
    }
  }

  /**
   * 删除技能
   */
  const deleteSkill = async (id: number) => {
    loading.value = true
    try {
      await skillsApi.deleteSkill(id)
      skills.value = skills.value.filter((s) => s.id !== id)
      if (currentSkill.value?.id === id) {
        currentSkill.value = null
      }
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

  return {
    skills,
    currentSkill,
    loading,
    total,
    fetchSkills,
    fetchSkill,
    createSkill,
    updateSkill,
    deleteSkill,
    clearCurrentSkill,
  }
})
