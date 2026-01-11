<template>
  <div class="agent-detail-view">
    <el-page-header @back="$router.back()" title="返回" content="代理详情" />
    <el-card class="detail-card" v-loading="agentsStore.loading">
      <template v-if="agentsStore.currentAgent">
        <h1>{{ agentsStore.currentAgent.name }}</h1>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ agentsStore.currentAgent.id }}</el-descriptions-item>
          <el-descriptions-item label="模型">{{ agentsStore.currentAgent.model_name }}</el-descriptions-item>
          <el-descriptions-item label="温度">{{ agentsStore.currentAgent.temperature }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="agentsStore.currentAgent.is_active ? 'success' : 'info'">
              {{ agentsStore.currentAgent.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <h2>关联技能</h2>
        <el-tag v-for="skill in agentsStore.currentAgent.skills" :key="skill.id" style="margin-right: 10px">
          {{ skill.name }}
        </el-tag>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAgentsStore } from '@/stores'

const route = useRoute()
const agentsStore = useAgentsStore()

onMounted(() => {
  const id = Number(route.params.id)
  agentsStore.fetchAgent(id)
})
</script>

<style scoped>
.agent-detail-view {
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
