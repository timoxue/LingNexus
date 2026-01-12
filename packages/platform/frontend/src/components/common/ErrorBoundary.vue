<template>
  <div class="error-boundary">
    <slot v-if="!hasError"></slot>

    <div v-else class="error-container">
      <el-result icon="error" :title="errorTitle" :sub-title="errorMessage">
        <template #extra>
          <el-button type="primary" @click="retry">
            {{ retryText }}
          </el-button>
          <el-button v-if="showHome" @click="goHome">
            返回首页
          </el-button>
        </template>
      </el-result>

      <!-- 错误详情（开发环境） -->
      <el-collapse v-if="isDev && errorDetails" class="error-details">
        <el-collapse-item title="错误详情">
          <pre>{{ errorDetails }}</pre>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

interface Props {
  title?: string
  message?: string
  retryText?: string
  showHome?: boolean
  onError?: (error: Error) => void
  resetKeys?: any[]
}

const props = withDefaults(defineProps<Props>(), {
  title: '出错了',
  message: '抱歉，应用程序遇到了一些问题',
  retryText: '重试',
  showHome: true,
  resetKeys: () => []
})

const emit = defineEmits<{
  error: [error: Error]
}>()

const router = useRouter()
const hasError = ref(false)
const error = ref<Error | null>(null)
const errorInfo = ref<any>(null)

const isDev = computed(() => import.meta.env.DEV)

const errorTitle = computed(() => {
  return props.title
})

const errorMessage = computed(() => {
  if (errorInfo.value?.message) {
    return errorInfo.value.message
  }
  return props.message
})

const errorDetails = computed(() => {
  if (!error.value) return null
  return JSON.stringify({
    message: error.value.message,
    stack: error.value.stack,
    info: errorInfo.value
  }, null, 2)
})

// 捕获错误
const captureError = (err: Error, info?: any) => {
  hasError.value = true
  error.value = err
  errorInfo.value = info

  // 触发回调
  if (props.onError) {
    props.onError(err)
  }

  // 触发事件
  emit('error', err)

  // 上报错误（可选）
  reportError(err, info)
}

// 重试
const retry = () => {
  hasError.value = false
  error.value = null
  errorInfo.value = null
}

// 返回首页
const goHome = () => {
  router.push('/')
}

// 错误上报（示例）
const reportError = (err: Error, info?: any) => {
  // TODO: 集成错误上报服务（如 Sentry）
  console.error('Error captured:', err, info)
}

// 暴露方法给父组件
defineExpose({
  captureError
})
</script>

<style scoped>
.error-boundary {
  width: 100%;
  height: 100%;
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 20px;
}

.error-details {
  margin-top: 20px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.error-details pre {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  line-height: 1.5;
}
</style>
