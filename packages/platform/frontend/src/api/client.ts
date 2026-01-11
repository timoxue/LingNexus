/**
 * API 客户端基础配置
 */
import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

// API 基础 URL
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

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
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理错误
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error: AxiosError) => {
    if (error.response) {
      const status = error.response.status

      // 401: 未授权，跳转到登录页
      if (status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }

      // 403: 禁止访问
      if (status === 403) {
        console.error('Access forbidden')
      }

      // 404: 资源不存在
      if (status === 404) {
        console.error('Resource not found')
      }

      // 500: 服务器错误
      if (status === 500) {
        console.error('Server error')
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
