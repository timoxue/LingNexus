/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '@/api/auth'
import type { User } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const is_superuser = computed(() => user.value?.is_superuser ?? false)
  const username = computed(() => user.value?.username ?? '')
  const email = computed(() => user.value?.email ?? '')

  /**
   * 登录
   */
  const login = async (username: string, password: string) => {
    loading.value = true
    try {
      const response = await authApi.login({ username, password })
      token.value = response.access_token
      user.value = response.user
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      return response
    } finally {
      loading.value = false
    }
  }

  /**
   * 注册
   */
  const register = async (data: {
    username: string
    email: string
    password: string
    full_name?: string
  }) => {
    loading.value = true
    try {
      const response = await authApi.register(data)
      token.value = response.access_token
      user.value = response.user
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      return response
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取当前用户信息
   */
  const fetchCurrentUser = async () => {
    if (!token.value) return

    loading.value = true
    try {
      user.value = await authApi.getCurrentUser()
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch (error) {
      // Token 可能已过期，清除本地存储
      logout()
    } finally {
      loading.value = false
    }
  }

  /**
   * 登出
   */
  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
    }
  }

  /**
   * 初始化：从本地存储恢复用户信息
   */
  const initialize = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch {
        localStorage.removeItem('user')
      }
    }
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    is_superuser,
    username,
    email,
    login,
    register,
    fetchCurrentUser,
    logout,
    initialize,
  }
})
