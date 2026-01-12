/**
 * API 客户端基础配置
 */
import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types'

// API 基础 URL
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// 请求重试配置
interface RetryConfig {
  retries: number
  retryDelay: number
  retryCondition?: (error: AxiosError) => boolean
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  retries: 3,
  retryDelay: 1000,
  retryCondition: (error: AxiosError) => {
    // 只对网络错误和5xx错误重试
    return !error.response || (error.response.status >= 500 && error.response.status < 600)
  }
}

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：添加 Token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 添加请求时间戳用于追踪
    config.metadata = { startTime: new Date() }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 扩展 Axios 配置以支持重试
declare module 'axios' {
  interface InternalAxiosRequestConfig {
    metadata?: {
      startTime: Date
    }
    _retry?: number
    _retryConfig?: RetryConfig
  }
}

// 响应拦截器：处理错误和重试
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // 计算请求耗时
    if (response.config.metadata) {
      const duration = new Date().getTime() - response.config.metadata.startTime.getTime()
      response.config.metadata['duration'] = duration
    }

    // 检查业务逻辑错误
    const data = response.data as ApiResponse
    if (data.success === false && data.error) {
      // 业务错误但HTTP状态码是200
      ElMessage.error({
        message: data.error.message,
        duration: 5000,
        grouping: true
      })
      return Promise.reject(new Error(data.error.message))
    }

    return response
  },
  async (error: AxiosError) => {
    const config = error.config as InternalAxiosRequestConfig

    // 重试逻辑
    if (config && DEFAULT_RETRY_CONFIG.retryCondition?.(error)) {
      config._retry = config._retry || 0
      const retryConfig = config._retryConfig || DEFAULT_RETRY_CONFIG

      if (config._retry < retryConfig.retries) {
        config._retry++
        console.log(`Retrying request (attempt ${config._retry}/${retryConfig.retries})...`)

        // 指数退避
        const delay = retryConfig.retryDelay * Math.pow(2, config._retry - 1)
        await new Promise(resolve => setTimeout(resolve, delay))

        return apiClient(config)
      }
    }

    if (error.response) {
      const status = error.response.status
      const data = error.response.data as ApiResponse

      // 使用服务器返回的错误信息（如果有）
      const errorMessage = data.error?.message || getErrorMessage(status)

      // 401: 未授权，跳转到登录页
      if (status === 401) {
        ElMessage.warning({
          message: '登录已过期，请重新登录',
          duration: 3000
        })
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(error)
      }

      // 403: 禁止访问
      if (status === 403) {
        ElMessage.error({
          message: data.error?.message || '权限不足',
          duration: 5000
        })
      }

      // 404: 资源不存在
      if (status === 404) {
        ElMessage.error({
          message: data.error?.message || '请求的资源不存在',
          duration: 5000
        })
      }

      // 429: 请求过于频繁
      if (status === 429) {
        ElMessage.warning({
          message: '请求过于频繁，请稍后再试',
          duration: 5000
        })
      }

      // 500: 服务器错误
      if (status >= 500) {
        ElMessage.error({
          message: '服务器错误，请稍后重试',
          duration: 5000
        })
      }

      // 记录错误
      console.error('API Error:', {
        status,
        message: errorMessage,
        url: config?.url,
        method: config?.method
      })
    } else if (error.request) {
      // 请求已发出但没有收到响应
      ElMessage.error({
        message: '网络连接失败，请检查网络设置',
        duration: 5000
      })
      console.error('Network Error:', error.message)
    } else {
      // 请求配置出错
      ElMessage.error({
        message: '请求配置错误',
        duration: 5000
      })
      console.error('Request Config Error:', error.message)
    }

    return Promise.reject(error)
  }
)

/**
 * 获取错误消息
 */
function getErrorMessage(status: number): string {
  const messages: Record<number, string> = {
    400: '请求参数错误',
    401: '未授权，请登录',
    403: '权限不足',
    404: '资源不存在',
    405: '请求方法不允许',
    409: '资源冲突',
    413: '请求实体过大',
    415: '不支持的媒体类型',
    422: '请求参数验证失败',
    429: '请求过于频繁',
    500: '服务器内部错误',
    502: '网关错误',
    503: '服务不可用',
    504: '网关超时'
  }
  return messages[status] || '请求失败'
}

export default apiClient
export { DEFAULT_RETRY_CONFIG }
export type { RetryConfig }
