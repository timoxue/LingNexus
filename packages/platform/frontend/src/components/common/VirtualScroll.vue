<!--
Virtual Scroll Component
Efficiently renders large lists by only visible items
-->
<template>
  <div
    ref="containerRef"
    class="virtual-scroll-container"
    :style="{ height: `${height}px` }"
    @scroll="handleScroll"
  >
    <div
      class="virtual-scroll-content"
      :style="{ height: `${totalHeight}px`, paddingTop: `${offsetY}px` }"
    >
      <div
        v-for="item in visibleItems"
        :key="getItemKey(item)"
        :ref="(el) => setItemRef(el, item)"
        class="virtual-scroll-item"
        :style="{ minHeight: `${itemHeight}px` }"
      >
        <slot :item="item" :index="getItemIndex(item)" />
      </div>
    </div>

    <div v-if="loading" class="virtual-scroll-loading">
      <slot name="loading">
        <Loading :visible="true" text="加载中..." />
      </slot>
    </div>

    <div v-if="!hasMore && items.length === 0" class="virtual-scroll-empty">
      <slot name="empty">
        <Empty />
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts" generic="T extends { id?: number | string }">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import Loading from './Loading.vue'
import Empty from './Empty.vue'

interface Props {
  items: T[]
  itemHeight?: number
  height?: number
  buffer?: number
  keyField?: string
  loading?: boolean
  hasMore?: boolean
  loadMore?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  itemHeight: 50,
  height: 400,
  buffer: 5,
  keyField: 'id',
  loading: false,
  hasMore: true
})

const emit = defineEmits<{
  scroll: [{ scrollTop: number; scrollDirection: 'up' | 'down' }]
}>()

// Refs
const containerRef = ref<HTMLElement>()
const itemRefs = new Map<T | number | string, HTMLElement>()

// State
const scrollTop = ref(0)
const lastScrollTop = ref(0)
const scrollDirection = ref<'up' | 'down'>('down')

// Computed
const totalHeight = computed(() => props.items.length * props.itemHeight)

const startIndex = computed(() => {
  const index = Math.floor(scrollTop.value / props.itemHeight)
  return Math.max(0, index - props.buffer)
})

const endIndex = computed(() => {
  const visibleCount = Math.ceil(props.height / props.itemHeight)
  const index = startIndex.value + visibleCount + props.buffer * 2
  return Math.min(props.items.length, index)
})

const offsetY = computed(() => startIndex.value * props.itemHeight)

const visibleItems = computed(() => {
  return props.items.slice(startIndex.value, endIndex.value)
})

// Methods
const getItemKey = (item: T): string | number => {
  return (item as any)[props.keyField] || JSON.stringify(item)
}

const getItemIndex = (item: T): number => {
  return props.items.indexOf(item)
}

const setItemRef = (el: any, item: T) => {
  if (el) {
    itemRefs.set(getItemKey(item), el)
  }
}

const handleScroll = (event: Event) => {
  const target = event.target as HTMLElement
  scrollTop.value = target.scrollTop

  // Detect scroll direction
  if (scrollTop.value > lastScrollTop.value) {
    scrollDirection.value = 'down'
  } else if (scrollTop.value < lastScrollTop.value) {
    scrollDirection.value = 'up'
  }

  lastScrollTop.value = scrollTop.value

  emit('scroll', {
    scrollTop: scrollTop.value,
    scrollDirection: scrollDirection.value
  })

  // Trigger load more when near bottom
  if (props.loadMore && props.hasMore && !props.loading) {
    const scrollHeight = target.scrollHeight
    const clientHeight = target.clientHeight
    const threshold = 100 // pixels from bottom

    if (scrollHeight - scrollTop.value - clientHeight < threshold) {
      props.loadMore()
    }
  }
}

const scrollToItem = (item: T) => {
  const index = getItemIndex(item)
  if (index !== -1 && containerRef.value) {
    const targetScrollTop = index * props.itemHeight
    containerRef.value.scrollTo({
      top: targetScrollTop,
      behavior: 'smooth'
    })
  }
}

const scrollToTop = () => {
  if (containerRef.value) {
    containerRef.value.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  }
}

const scrollToBottom = () => {
  if (containerRef.value) {
    containerRef.value.scrollTo({
      top: totalHeight.value,
      behavior: 'smooth'
    })
  }
}

// Lifecycle
onMounted(() => {
  if (containerRef.value) {
    containerRef.value.addEventListener('scroll', handleScroll, { passive: true })
  }
})

onUnmounted(() => {
  if (containerRef.value) {
    containerRef.value.removeEventListener('scroll', handleScroll)
  }
})

// Watch for items changes
watch(
  () => props.items.length,
  () => {
    // Recalculate if needed
    nextTick(() => {
      // Force update
    })
  }
)

// Expose methods
defineExpose({
  scrollToItem,
  scrollToTop,
  scrollToBottom
})
</script>

<style scoped>
.virtual-scroll-container {
  position: relative;
  overflow-y: auto;
  overflow-x: hidden;
}

.virtual-scroll-content {
  box-sizing: border-box;
}

.virtual-scroll-item {
  box-sizing: border-box;
}

.virtual-scroll-loading {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  text-align: center;
  background: linear-gradient(transparent, rgba(255, 255, 255, 0.9));
}

.virtual-scroll-empty {
  padding: 40px;
  text-align: center;
}

/* Custom scrollbar */
.virtual-scroll-container::-webkit-scrollbar {
  width: 8px;
}

.virtual-scroll-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.virtual-scroll-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.virtual-scroll-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
