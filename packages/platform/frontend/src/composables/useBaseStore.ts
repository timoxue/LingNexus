/**
 * Base store composable with common functionality
 * Provides error handling, loading states, and optimistic updates
 */
import { ref, shallowRef } from 'vue'
import { useErrorHandler } from './useErrorHandler'

export interface PaginationState {
  page: number
  pageSize: number
  total: number
}

export interface RequestOptions {
  silent?: boolean
  optimistic?: boolean
}

/**
 * Base store composable for consistent state management
 */
export function useBaseStore<T extends { id: number | string }>(storeName: string) {
  const { handleError } = useErrorHandler()

  // State
  const items = shallowRef<T[]>([])
  const currentItem = shallowRef<T | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const pagination = ref<PaginationState>({
    page: 1,
    pageSize: 20,
    total: 0
  })

  // Pending requests map for deduplication
  const pendingRequests = new Map<string, Promise<any>>()

  /**
   * Execute async operation with error handling
   */
  const executeAsync = async <R>(
    operation: () => Promise<R>,
    options: RequestOptions = {}
  ): Promise<R | null> => {
    const { silent = false } = options

    loading.value = true
    error.value = null

    try {
      const result = await operation()
      return result
    } catch (err) {
      const { message } = handleError(err, {
        showMessage: !silent,
        logToConsole: true
      })
      error.value = message
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Deduplicate concurrent requests
   */
  const deduplicateRequest = <R>(
    key: string,
    requestFn: () => Promise<R>
  ): Promise<R> => {
    if (pendingRequests.has(key)) {
      return pendingRequests.get(key)!
    }

    const promise = requestFn().finally(() => {
      pendingRequests.delete(key)
    })

    pendingRequests.set(key, promise)
    return promise
  }

  /**
   * Optimistically update items list
   */
  const optimisticUpdate = (
    id: number | string,
    updates: Partial<T>,
    temporaryId?: number | string
  ) => {
    if (temporaryId) {
      // Add temporary item
      const tempItem = { ...updates, id: temporaryId } as T
      items.value.unshift(tempItem)
    } else {
      // Update existing item
      const index = items.value.findIndex((item) => item.id === id)
      if (index !== -1) {
        items.value[index] = { ...items.value[index], ...updates }
      }
    }
  }

  /**
   * Revert optimistic update
   */
  const revertOptimisticUpdate = (id: number | string, temporaryId?: number | string) => {
    if (temporaryId) {
      // Remove temporary item
      items.value = items.value.filter((item) => item.id !== temporaryId)
    } else {
      // Revert by re-fetching or restore from backup
      // Implementation depends on use case
    }
  }

  /**
   * Update items in list
   */
  const updateItems = (newItems: T[]) => {
    items.value = newItems
  }

  /**
   * Add single item to list
   */
  const addItem = (item: T) => {
    items.value.unshift(item)
  }

  /**
   * Update single item in list
   */
  const updateItem = (id: number | string, updates: Partial<T>) => {
    const index = items.value.findIndex((item) => item.id === id)
    if (index !== -1) {
      items.value[index] = { ...items.value[index], ...updates }
    }
    // Also update current item if matches
    if (currentItem.value?.id === id) {
      currentItem.value = { ...currentItem.value, ...updates } as T
    }
  }

  /**
   * Remove item from list
   */
  const removeItem = (id: number | string) => {
    items.value = items.value.filter((item) => item.id !== id)
    if (currentItem.value?.id === id) {
      currentItem.value = null
    }
  }

  /**
   * Set current item
   */
  const setCurrentItem = (item: T | null) => {
    currentItem.value = item
  }

  /**
   * Update pagination
   */
  const updatePagination = (updates: Partial<PaginationState>) => {
    pagination.value = { ...pagination.value, ...updates }
  }

  /**
   * Reset all state
   */
  const reset = () => {
    items.value = []
    currentItem.value = null
    loading.value = false
    error.value = null
    pagination.value = {
      page: 1,
      pageSize: 20,
      total: 0
    }
    pendingRequests.clear()
  }

  return {
    // State
    items,
    currentItem,
    loading,
    error,
    pagination,

    // Methods
    executeAsync,
    deduplicateRequest,
    optimisticUpdate,
    revertOptimisticUpdate,
    updateItems,
    addItem,
    updateItem,
    removeItem,
    setCurrentItem,
    updatePagination,
    reset
  }
}

/**
 * Create a cache key for requests
 */
export function createCacheKey(storeName: string, action: string, params?: any): string {
  const paramsStr = params ? JSON.stringify(params) : ''
  return `${storeName}:${action}:${paramsStr}`
}
