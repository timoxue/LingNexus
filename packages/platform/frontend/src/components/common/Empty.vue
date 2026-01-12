<template>
  <div class="empty-container">
    <div class="empty-content">
      <!-- 图标 -->
      <div class="empty-icon">
        <slot name="icon">
          <el-icon :size="iconSize">
            <component :is="iconComponent" />
          </el-icon>
        </slot>
      </div>

      <!-- 标题 -->
      <div class="empty-title">
        {{ title }}
      </div>

      <!-- 描述 -->
      <div v-if="description" class="empty-description">
        {{ description }}
      </div>

      <!-- 操作按钮 -->
      <div v-if="$slots.action" class="empty-action">
        <slot name="action"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Document, Picture, FolderOpened, Warning } from '@element-plus/icons-vue'

interface Props {
  type?: 'data' | 'image' | 'folder' | 'error' | 'custom'
  title?: string
  description?: string
  iconSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  type: 'data',
  title: '暂无数据',
  description: '',
  iconSize: 64
})

const iconMap = {
  data: Document,
  image: Picture,
  folder: FolderOpened,
  error: Warning,
  custom: Document
}

const iconComponent = computed(() => {
  return iconMap[props.type] || iconMap.custom
})
</script>

<style scoped>
.empty-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  min-height: 200px;
}

.empty-content {
  text-align: center;
}

.empty-icon {
  margin-bottom: 16px;
  color: #909399;
}

.empty-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}

.empty-description {
  font-size: 14px;
  color: #909399;
  margin-bottom: 16px;
  line-height: 1.5;
}

.empty-action {
  margin-top: 16px;
}
</style>
