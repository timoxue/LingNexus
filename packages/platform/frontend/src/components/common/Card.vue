<template>
  <el-card
    :shadow="shadow"
    :body-style="bodyStyle"
    :class="['custom-card', { 'is-hoverable': hoverable, 'is-border': border }]"
  >
    <!-- 头部 -->
    <template v-if="$slots.header || title" #header>
      <div class="card-header">
        <div class="header-left">
          <slot name="icon">
            <el-icon v-if="icon" :size="20">
              <component :is="icon" />
            </el-icon>
          </slot>
          <span class="card-title">{{ title }}</span>
          <slot name="extra"></slot>
        </div>
        <div v-if="$slots.action" class="header-right">
          <slot name="action"></slot>
        </div>
      </div>
    </template>

    <!-- 内容 -->
    <div class="card-body">
      <slot></slot>
    </div>

    <!-- 底部 -->
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </el-card>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  icon?: any
  shadow?: 'always' | 'hover' | 'never'
  hoverable?: boolean
  border?: boolean
  bodyStyle?: any
}

withDefaults(defineProps<Props>(), {
  shadow: 'never',
  hoverable: false,
  border: false,
  bodyStyle: () => ({})
})
</script>

<style scoped>
.custom-card {
  transition: all 0.3s ease;
}

.custom-card.is-hoverable:hover {
  transform: translateY(-2px);
}

.custom-card.is-border {
  border: 1px solid #dcdfe6;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-body {
  flex: 1;
}

.card-footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
