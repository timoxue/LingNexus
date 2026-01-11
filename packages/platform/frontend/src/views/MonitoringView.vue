<template>
  <div class="monitoring-view">
    <div class="header">
      <h1>监控数据</h1>
      <el-button type="primary" @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ statistics?.projects?.total || 0 }}</div>
            <div class="stat-label">监控项目</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ statistics?.projects?.active || 0 }}</div>
            <div class="stat-label">活跃项目</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ statistics?.trials?.total || 0 }}</div>
            <div class="stat-label">临床试验总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ Object.keys(statistics?.trials?.by_source || {}).length }}</div>
            <div class="stat-label">数据源</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 监控项目列表 -->
    <el-card class="projects-card">
      <template #header>
        <div class="card-header">
          <span>监控项目</span>
          <el-button type="primary" size="small">创建项目</el-button>
        </div>
      </template>
      <el-table v-loading="monitoringStore.loading" :data="monitoringStore.projects" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="keywords" label="关键词" width="300">
          <template #default="{ row }">
            <el-tag v-for="keyword in row.keywords.slice(0, 3)" :key="keyword" size="small" style="margin-right: 5px">
              {{ keyword }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="trial_count" label="试验数量" width="100" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '活跃' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewProject(row)">查看</el-button>
            <el-button link type="primary" @click="editProject(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMonitoringStore } from '@/stores'
import { Refresh } from '@element-plus/icons-vue'
import type { MonitoringProject } from '@/api/monitoring'

const router = useRouter()
const monitoringStore = useMonitoringStore()

const statistics = ref()

// 刷新数据
const refreshData = async () => {
  await monitoringStore.fetchProjects()
  statistics.value = await monitoringStore.fetchStatistics()
}

// 查看项目
const viewProject = (project: MonitoringProject) => {
  router.push({ name: 'MonitoringProjectDetail', params: { id: project.id } })
}

// 编辑项目
const editProject = (project: MonitoringProject) => {
  // TODO: 实现编辑功能
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.monitoring-view {
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0;
  color: #303133;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 10px;
}

.projects-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
