/**
 * 全局错误处理插件
 */
import { type App } from 'vue'
import { ElMessage } from 'element-plus'
import type { Router } from 'vue-router'
import type { ApiResponse } from '@/types'

/**
 * 处理API错误响应
 */
export function handleApiError(response: ApiResponse): void {
  if (!response.success && response.error) {
    ElMessage.error({
      message: response.error.message,
      duration: 5000,
      grouping: true
    })
  }
}

/**
 * 处理路由错误
 */
export function handleRouteError(error: any): void {
  console.error('Route error:', error)

  ElMessage.error({
    message: '页面加载失败',
    duration: 5000
  })
}

/**
 * 全局错误处理
 */
export function setupGlobalErrorHandler(app: App, router: Router) {
  // Vue错误
  app.config.errorHandler = (err, instance, info) => {
    console.error('Vue error:', err, info)

    // 避免重复提示
    if (err && !err.__handled) {
      ElMessage.error({
        message: '应用发生错误，请刷新页面重试',
        duration: 5000
      })
      err.__handled = true
    }
  }

  // 警告
  app.config.warnHandler = (msg, instance, trace) => {
    console.warn('Vue warning:', msg, trace)
  }

  // 路由错误
  router.onError((error) => {
    handleRouteError(error)
  })

  // 未捕获的Promise错误
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled rejection:', event.reason)

    event.preventDefault()
  })

  // 全局错误捕获
  window.addEventListener('error', (event) => {
    console.error('Global error:', event.error)
  })
}
