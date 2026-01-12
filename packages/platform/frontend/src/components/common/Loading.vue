<template>
  <div v-if="visible" class="loading-container" :class="{ fullscreen, inline }">
    <div class="loading-content">
      <!-- Spinner -->
      <div v-if="!text" class="spinner">
        <div class="bounce1"></div>
        <div class="bounce2"></div>
        <div class="bounce3"></div>
      </div>

      <!-- Text -->
      <div v-if="text" class="loading-text">
        {{ text }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  visible?: boolean
  fullscreen?: boolean
  inline?: boolean
  text?: string
  delay?: number // 延迟显示（毫秒）
}

withDefaults(defineProps<Props>(), {
  visible: true,
  fullscreen: false,
  inline: false,
  text: '',
  delay: 0
})

// 延迟显示逻辑
const show = ref(props.delay > 0 ? false : true)

if (props.delay > 0) {
  setTimeout(() => {
    show.value = true
  }, props.delay)
}
</script>

<style scoped>
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-container.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  z-index: 9999;
}

.loading-container.inline {
  display: inline-flex;
}

.loading-content {
  text-align: center;
}

/* Bounce Animation */
.spinner {
  display: flex;
  justify-content: center;
}

.spinner > div {
  width: 12px;
  height: 12px;
  background-color: #409eff;
  border-radius: 100%;
  display: inline-block;
  animation: bounce 1.4s infinite ease-in-out both;
}

.spinner .bounce1 {
  animation-delay: -0.32s;
}

.spinner .bounce2 {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.loading-text {
  margin-top: 12px;
  color: #606266;
  font-size: 14px;
}
</style>
