<!--
Lazy Image Component
Automatically loads images when they enter the viewport
-->
<template>
  <div class="lazy-image-wrapper" :class="{ 'is-loaded': loaded, 'has-error': hasError }" :style="wrapperStyle">
    <img
      v-if="!hasError"
      :src="currentSrc"
      :alt="alt"
      :class="imageClass"
      :style="imageStyle"
      @load="handleLoad"
      @error="handleError"
      v-lazy="src"
    />

    <!-- Loading Placeholder -->
    <div v-if="!loaded && !hasError" class="lazy-image-placeholder">
      <slot name="placeholder">
        <div class="default-placeholder">
          <slot name="loading">
            <span class="loading-spinner"></span>
          </slot>
        </div>
      </slot>
    </div>

    <!-- Error Placeholder -->
    <div v-if="hasError" class="lazy-image-error">
      <slot name="error">
        <div class="default-error">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
            <circle cx="8.5" cy="8.5" r="1.5" />
            <polyline points="21 15 16 10 5 21" />
          </svg>
          <span>加载失败</span>
        </div>
      </slot>
    </div>

    <!-- Fade Overlay -->
    <div v-if="fade && loaded" class="lazy-image-fade-overlay" :class="{ 'fade-out': loaded }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Props {
  src: string
  alt?: string
  width?: number | string
  height?: number | string
  fit?: 'contain' | 'cover' | 'fill' | 'none' | 'scale-down'
  imageClass?: string
  imageStyle?: Record<string, any>
  fade?: boolean
  eager?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  alt: '',
  fit: 'cover',
  imageClass: '',
  imageStyle: () => ({}),
  fade: true,
  eager: false
})

const emit = defineEmits<{
  load: [event: Event]
  error: [event: Event]
}>()

// State
const loaded = ref(false)
const hasError = ref(false)
const currentSrc = ref('')

// Computed
const wrapperStyle = computed(() => {
  const style: Record<string, any> = {}

  if (props.width) {
    style.width = typeof props.width === 'number' ? `${props.width}px` : props.width
  }

  if (props.height) {
    style.height = typeof props.height === 'number' ? `${props.height}px` : props.height
  }

  return style
})

// Methods
const handleLoad = (event: Event) => {
  loaded.value = true
  hasError.value = false
  emit('load', event)
}

const handleError = (event: Event) => {
  hasError.value = true
  loaded.value = false
  emit('error', event)
}

const loadImage = () => {
  if (!props.src) return

  currentSrc.value = props.src
  loaded.value = false
  hasError.value = false
}

// Watch for src changes
watch(
  () => props.src,
  () => {
    loadImage()
  },
  { immediate: !props.eager }
)

// Initial load
if (props.eager) {
  loadImage()
}
</script>

<style scoped>
.lazy-image-wrapper {
  position: relative;
  overflow: hidden;
  display: inline-block;
  background-color: #f5f5f5;
}

.lazy-image-wrapper img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: v-bind('props.fit');
  opacity: 0;
  transition: opacity 0.3s ease-in-out;
}

.lazy-image-wrapper.is-loaded img {
  opacity: 1;
}

.lazy-image-placeholder,
.lazy-image-error {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.default-placeholder,
.default-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #999;
}

.loading-spinner {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: #409eff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.default-error svg {
  width: 48px;
  height: 48px;
  stroke: #999;
}

.lazy-image-fade-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: white;
  pointer-events: none;
  transition: opacity 0.5s ease-in-out;
}

.lazy-image-fade-overlay.fade-out {
  opacity: 0;
}

.has-error {
  background-color: #fafafa;
}
</style>
