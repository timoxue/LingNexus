<template>
  <div class="agent-detail-view">
    <el-page-header @back="$router.back()" title="返回" content="Agent 详情" />

    <el-card class="detail-card" v-loading="agentsStore.loading">
      <template v-if="agentsStore.currentAgent">
        <!-- Agent 基本信息 -->
        <div class="agent-header">
          <div class="agent-info">
            <h1>{{ agentsStore.currentAgent.name }}</h1>
            <p v-if="agentsStore.currentAgent.description" class="description">
              {{ agentsStore.currentAgent.description }}
            </p>
          </div>
          <div class="agent-actions">
            <el-button type="success" @click="showExecuteDialog = true">
              <el-icon><VideoPlay /></el-icon>
              执行 Agent
            </el-button>
            <el-button @click="$router.push({ name: 'Agents', query: { edit: agentsStore.currentAgent.id } })">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
          </div>
        </div>

        <el-descriptions :column="3" border class="agent-meta">
          <el-descriptions-item label="模型">{{ agentsStore.currentAgent.model_name }}</el-descriptions-item>
          <el-descriptions-item label="温度">{{ agentsStore.currentAgent.temperature }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="agentsStore.currentAgent.is_active ? 'success' : 'info'">
              {{ agentsStore.currentAgent.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="最大 Token">
            {{ agentsStore.currentAgent.max_tokens || '默认' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ formatDate(agentsStore.currentAgent.created_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 关联技能 -->
        <div class="section">
          <h3>关联技能</h3>
          <div v-if="agentsStore.currentAgent.skills.length > 0" class="skills-list">
            <el-tag
              v-for="skill in agentsStore.currentAgent.skills"
              :key="skill.id"
              :type="skill.category === 'external' ? 'primary' : 'warning'"
              size="large"
            >
              {{ skill.name }}
            </el-tag>
          </div>
          <el-empty v-else description="暂无关联技能" :image-size="80" />
        </div>

        <!-- 系统提示 -->
        <div v-if="agentsStore.currentAgent.system_prompt" class="section">
          <h3>系统提示</h3>
          <el-input
            type="textarea"
            :model-value="agentsStore.currentAgent.system_prompt"
            :rows="4"
            readonly
          />
        </div>

        <!-- 执行历史 -->
        <div class="section">
          <div class="section-header">
            <h3>执行历史</h3>
            <el-button size="small" @click="loadExecutions">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>

          <el-table
            v-loading="loadingExecutions"
            :data="agentsStore.executions"
            stripe
            @row-click="viewExecution"
            style="cursor: pointer"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="input_message" label="输入消息" show-overflow-tooltip />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Token 使用" width="120">
              <template #default="{ row }">
                {{ row.tokens_used || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="执行时间" width="120">
              <template #default="{ row }">
                {{ row.execution_time ? `${row.execution_time.toFixed(2)}s` : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>

          <el-empty
            v-if="!loadingExecutions && agentsStore.executions.length === 0"
            description="暂无执行记录"
            :image-size="80"
          />
        </div>
      </template>
    </el-card>

    <!-- 执行对话框 -->
    <el-dialog
      v-model="showExecuteDialog"
      title="执行 Agent"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="agentsStore.currentAgent">
        <!-- Agent 信息 -->
        <el-alert
          :title="`正在执行: ${agentsStore.currentAgent.name}`"
          type="info"
          :closable="false"
          show-icon
        />

        <el-divider />

        <!-- 输入区域 -->
        <el-form label-width="80px">
          <el-form-item label="消息">
            <el-input
              v-model="executeMessage"
              type="textarea"
              :rows="4"
              placeholder="请输入要发送给 Agent 的消息"
              :disabled="executing"
            />
          </el-form-item>
        </el-form>

        <!-- 执行结果 -->
        <div v-if="executeResult" class="execute-result">
          <el-divider />
          <h4>执行结果</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="状态">
              <el-tag :type="executeResult.status === 'success' ? 'success' : 'danger'">
                {{ executeResult.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="执行时间">
              {{ executeResult.execution_time?.toFixed(2) }}秒
            </el-descriptions-item>
            <el-descriptions-item label="Token 使用" :span="2">
              {{ executeResult.tokens_used }}
            </el-descriptions-item>
          </el-descriptions>

          <!-- 输出消息 -->
          <div v-if="executeResult.output_message" class="result-content">
            <h5>输出:</h5>
            <div class="message-box">{{ executeResult.output_message }}</div>
          </div>

          <!-- 错误消息 -->
          <div v-if="executeResult.error_message" class="error-content">
            <h5>错误:</h5>
            <div class="message-box error">{{ executeResult.error_message }}</div>
          </div>

          <!-- 生成的文件 -->
          <ArtifactList
            v-if="executeResult.artifacts && executeResult.artifacts.length > 0"
            :artifacts="executeResult.artifacts"
            class="artifact-section"
          />
        </div>
      </div>

      <template #footer>
        <el-button @click="closeExecuteDialog" :disabled="executing">关闭</el-button>
        <el-button
          type="primary"
          :loading="executing"
          @click="handleExecute"
          :disabled="!executeMessage.trim()"
        >
          执行
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行详情对话框 -->
    <el-dialog
      v-model="showExecutionDetailDialog"
      title="执行详情"
      width="800px"
    >
      <div v-if="selectedExecution">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="执行 ID">{{ selectedExecution.id }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedExecution.status)">
              {{ getStatusText(selectedExecution.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(selectedExecution.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间">
            {{ selectedExecution.completed_at ? formatDate(selectedExecution.completed_at) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="执行时间">
            {{ selectedExecution.execution_time ? `${selectedExecution.execution_time.toFixed(2)}秒` : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="Token 使用">
            {{ selectedExecution.tokens_used || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <div class="execution-detail">
          <h4>输入消息</h4>
          <div class="message-box">{{ selectedExecution.input_message }}</div>

          <div v-if="selectedExecution.output_message" class="detail-section">
            <h4>输出消息</h4>
            <div class="message-box">{{ selectedExecution.output_message }}</div>
          </div>

          <div v-if="selectedExecution.error_message" class="detail-section">
            <h4>错误消息</h4>
            <div class="message-box error">{{ selectedExecution.error_message }}</div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAgentsStore } from '@/stores'
import { ElMessage } from 'element-plus'
import { VideoPlay, Edit, Refresh } from '@element-plus/icons-vue'
import type { AgentExecution } from '@/api/agents'
import ArtifactList from '@/components/ArtifactList.vue'

const route = useRoute()
const agentsStore = useAgentsStore()

const showExecuteDialog = ref(false)
const showExecutionDetailDialog = ref(false)
const executeMessage = ref('')
const executing = ref(false)
const executeResult = ref<any>(null)
const loadingExecutions = ref(false)
const selectedExecution = ref<AgentExecution | null>(null)

// 格式化日期
const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    success: 'success',
    failed: 'danger',
    running: 'warning',
    pending: 'info',
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    success: '成功',
    failed: '失败',
    running: '运行中',
    pending: '等待中',
  }
  return texts[status] || status
}

// 加载执行历史
const loadExecutions = async () => {
  const id = Number(route.params.id)
  loadingExecutions.value = true
  try {
    await agentsStore.fetchExecutions(id, { limit: 50 })
  } finally {
    loadingExecutions.value = false
  }
}

// 查看执行详情
const viewExecution = (execution: AgentExecution) => {
  selectedExecution.value = execution
  showExecutionDetailDialog.value = true
}

// 执行 Agent
const handleExecute = async () => {
  if (!executeMessage.value.trim()) {
    ElMessage.warning('请输入执行消息')
    return
  }

  executing.value = true
  executeResult.value = null

  try {
    const result = await agentsStore.executeAgent(
      agentsStore.currentAgent!.id,
      { message: executeMessage.value }
    )

    executeResult.value = result

    if (result.status === 'success') {
      ElMessage.success('执行成功')
      // 刷新执行历史
      loadExecutions()
    } else {
      ElMessage.error('执行失败: ' + (result.error_message || '未知错误'))
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '执行失败')
  } finally {
    executing.value = false
  }
}

// 关闭执行对话框
const closeExecuteDialog = () => {
  showExecuteDialog.value = false
  executeMessage.value = ''
  executeResult.value = null
}

onMounted(async () => {
  const id = Number(route.params.id)
  await agentsStore.fetchAgent(id)
  await loadExecutions()
})
</script>

<style scoped>
.agent-detail-view {
  max-width: 1400px;
  margin: 0 auto;
}

.detail-card {
  margin-top: 20px;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.agent-info h1 {
  margin: 0 0 10px 0;
  color: #303133;
}

.agent-info .description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.agent-actions {
  display: flex;
  gap: 10px;
}

.agent-meta {
  margin-bottom: 20px;
}

.section {
  margin-top: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 18px;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.execute-result {
  margin-top: 20px;
}

.execute-result h4,
.execution-detail h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.execute-result h5 {
  margin: 10px 0 5px 0;
  color: #606266;
  font-size: 14px;
}

.result-content,
.error-content,
.detail-section {
  margin-top: 15px;
}

.message-box {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 14px;
  line-height: 1.6;
}

.message-box.error {
  background-color: #fef0f0;
  color: #f56c6c;
}

.execution-detail {
  margin-top: 20px;
}

.execution-detail h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.detail-section {
  margin-top: 20px;
}

:deep(.el-table__row) {
  transition: background-color 0.2s;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>
