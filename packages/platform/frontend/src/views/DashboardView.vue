<template>
  <div class="dashboard">
    <h1>仪表板</h1>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#409eff"><Files /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics?.skills_count || 0 }}</div>
              <div class="stat-label">技能总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#67c23a"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics?.agents_count || 0 }}</div>
              <div class="stat-label">代理总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#e6a23c"><Monitor /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics?.projects_count || 0 }}</div>
              <div class="stat-label">监控项目</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#f56c6c"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics?.trials_count || 0 }}</div>
              <div class="stat-label">临床试验</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 欢迎信息 -->
    <el-card class="welcome-card">
      <h2>欢迎来到 LingNexus Platform</h2>
      <p>低代码 AI 代理构建平台，帮助您快速创建和管理智能代理</p>

      <el-divider />

      <h3>快速开始</h3>
      <el-row :gutter="20">
        <el-col :span="8">
          <div class="quick-start-item">
            <el-icon size="40" color="#409eff"><Files /></el-icon>
            <h4>技能管理</h4>
            <p>管理和配置可复用的 AI 技能</p>
            <el-button type="primary" @click="$router.push('/skills')">查看技能</el-button>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="quick-start-item">
            <el-icon size="40" color="#67c23a"><User /></el-icon>
            <h4>代理管理</h4>
            <p>创建和配置您的 AI 代理</p>
            <el-button type="success" @click="$router.push('/agents')">查看代理</el-button>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="quick-start-item">
            <el-icon size="40" color="#e6a23c"><Monitor /></el-icon>
            <h4>监控数据</h4>
            <p>查看竞品情报监控数据</p>
            <el-button type="warning" @click="$router.push('/monitoring')">查看数据</el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Files, User, Monitor, Document } from '@element-plus/icons-vue'

// 统计数据（模拟数据，实际应从 API 获取）
const statistics = ref({
  skills_count: 12,
  agents_count: 5,
  projects_count: 3,
  trials_count: 156,
})

onMounted(() => {
  // TODO: 从 API 获取统计数据
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 20px;
  color: #303133;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  font-size: 48px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.welcome-card {
  margin-top: 20px;
}

.welcome-card h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.welcome-card p {
  margin: 0;
  color: #606266;
}

.welcome-card h3 {
  margin-top: 20px;
  color: #303133;
}

.quick-start-item {
  text-align: center;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.quick-start-item h4 {
  margin: 15px 0 10px 0;
  color: #303133;
}

.quick-start-item p {
  margin: 0 0 15px 0;
  color: #606266;
  font-size: 14px;
}
</style>
