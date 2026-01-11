<template>
  <div class="project-detail-view">
    <el-page-header @back="$router.back()" title="返回" content="监控项目详情" />
    <el-card class="detail-card" v-loading="monitoringStore.loading">
      <template v-if="monitoringStore.currentProject">
        <h1>{{ monitoringStore.currentProject.name }}</h1>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ monitoringStore.currentProject.id }}</el-descriptions-item>
          <el-descriptions-item label="试验数量">{{ monitoringStore.currentProject.trial_count }}</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <h2>关键词</h2>
        <el-tag v-for="keyword in monitoringStore.currentProject.keywords" :key="keyword" style="margin-right: 10px">
          {{ keyword }}
        </el-tag>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMonitoringStore } from '@/stores'

const route = useRoute()
const monitoringStore = useMonitoringStore()

onMounted(() => {
  const id = Number(route.params.id)
  monitoringStore.fetchProject(id)
})
</script>

<style scoped>
.project-detail-view {
  max-width: 1200px;
  margin: 0 auto;
}

.detail-card {
  margin-top: 20px;
}

h1 {
  margin: 0 0 20px 0;
  color: #303133;
}

h2 {
  margin: 20px 0 10px 0;
  color: #303133;
}
</style>
