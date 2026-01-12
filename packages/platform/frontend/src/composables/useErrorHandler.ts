/**
 * 全局错误处理 Composable
 */
import { ref, inject } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import type { ApiResponse } from '@/types'

interface ErrorOptions {
  showMessage?: boolean
  showNotification?: boolean
  duration?: number
  logToConsole?: boolean
}

const globalError = ref<Error | null>(null)

export function useErrorHandler() {
  /**
   * 处理API错误
   */
  const handleError = (
    error: Error | ApiResponse | unknown,
    options: ErrorOptions = {}
  ) => {
    const {
      showMessage = true,
      showNotification = false,
      duration = 5000,
      logToConsole = true
    } = options

    // 设置全局错误
    globalError.value = error instanceof Error ? error : null

    // 提取错误信息
    let message = '操作失败，请稍后重试'
    let code = 'UNKNOWN_ERROR'

    if (error instanceof Error) {
      message = error.message
    } else if (typeof error === 'object' && error !== null) {
      const apiResponse = error as ApiResponse
      if (apiResponse.error) {
        message = apiResponse.error.message
        code = apiResponse.error.code
      }
    } else if (typeof error === 'string') {
      message = error
    }

    // 记录到控制台
    if (logToConsole) {
      console.error(`[${code}]`, message, error)
    }

    // 显示消息
    if (showMessage) {
      ElMessage.error({
        message,
        duration,
        grouping: true
      })
    }

    // 显示通知
    if (showNotification) {
      ElNotification.error({
        title: '操作失败',
        message,
        duration
      })
    }

    return { message, code }
  }

  /**
   * 处理异步错误
   */
  const handleAsyncError = async <T>(
    asyncFn: () => Promise<T>,
    options: ErrorOptions = {}
  ): Promise<{ data: T | null; error: string | null }> => {
    try {
      const data = await asyncFn()
      return { data, error: null }
    } catch (err) {
      handleError(err, options)
      return { data: null, error: err instanceof Error ? err.message : String(err) }
    }
  }

  /**
   * 清除全局错误
   */
  const clearError = () => {
    globalError.value = null
  }

  return {
    globalError,
    handleError,
    handleAsyncError,
    clearError
  }
}

/**
 * 提供全局错误处理实例
 */
let globalErrorHandler: ReturnType<typeof useErrorHandler> | null = null

export function provideErrorHandler() {
  if (!globalErrorHandler) {
    globalErrorHandler = useErrorHandler()
  }
  return globalErrorHandler
}
