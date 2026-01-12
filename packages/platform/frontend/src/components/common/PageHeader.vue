<template>
  <div class="page-header">
    <div class="header-left">
      <!-- 返回按钮 -->
      <el-button
        v-if="showBack"
        class="back-button"
        :icon="ArrowLeft"
        circle
        @click="handleBack"
      />

      <!-- 标题 -->
      <div class="header-title">
        <h1>{{ title }}</h1>
        <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
      </div>
    </div>

    <div class="header-right">
      <!-- 右侧插槽 -->
      <slot name="extra"></slot>
    </div>

    <!-- 标签 -->
    <div v-if="$slots.tags" class="header-tags">
      <slot name="tags"></slot>
    </div>

    <!-- 分割线 -->
    <el-divider v-if="showDivider" />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'

interface Props {
  title?: string
  subtitle?: string
  showBack?: boolean
  showDivider?: boolean
  backTo?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  subtitle: '',
  showBack: false,
  showDivider: true
})

const emit = defineEmits<{
  back: []
}>()

const router = useRouter()

const handleBack = () => {
  if (props.backTo) {
    router.push(props.backTo)
  } else {
    router.back()
  }
  emit('back')
}
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-button {
  flex-shrink: 0;
}

.header-title {
  flex: 1;
}

.header-title h1 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.subtitle {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-tags {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
