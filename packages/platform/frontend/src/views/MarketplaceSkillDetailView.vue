<template>
  <div class="skill-detail-view" v-loading="marketplaceStore.loading">
    <div v-if="marketplaceStore.currentSkill" class="content">
      <!-- 头部 -->
      <div class="header">
        <el-button link @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div class="title-section">
          <div class="tags">
            <el-tag v-if="skill.is_official" type="success" effect="dark">官方认证</el-tag>
            <el-tag :type="skill.category === 'external' ? 'primary' : 'warning'">
              {{ skill.category === 'external' ? '外部技能' : '内部技能' }}
            </el-tag>
            <el-tag v-if="skill.sharing_scope === 'public'" type="success" plain>公开</el-tag>
            <el-tag v-else-if="skill.sharing_scope === 'team'" type="info" plain>团队</el-tag>
            <el-tag v-else type="warning" plain>私有</el-tag>
          </div>
          <h1>{{ skill.name }}</h1>
          <div class="meta">
            <span>创建者: {{ skill.creator_name || '未知' }}</span>
            <span>使用次数: {{ skill.usage_count }}</span>
            <span>版本: {{ skill.version }}</span>
          </div>
        </div>
      </div>

      <!-- 主要内容 -->
      <el-row :gutter="20">
        <el-col :span="16">
          <!-- 技能描述 -->
          <el-card class="detail-card">
            <template #header>
              <h3>技能描述</h3>
            </template>
            <div class="description">
              {{ skill.meta?.description || '暂无描述' }}
            </div>
          </el-card>

          <!-- 技能内容 -->
          <el-card class="detail-card">
            <template #header>
              <h3>技能内容</h3>
            </template>
            <pre class="skill-content">{{ skill.content }}</pre>
          </el-card>

          <!-- 使用文档 -->
          <el-card v-if="skill.documentation" class="detail-card">
            <template #header>
              <h3>使用文档</h3>
            </template>
            <div class="documentation" v-html="skill.documentation"></div>
          </el-card>

          <!-- 评分和评论 -->
          <el-card class="detail-card">
            <template #header>
              <h3>用户评分</h3>
            </template>
            <div class="rating-section">
              <div class="average-rating">
                <div class="rating-number">{{ skill.rating || '暂无评分' }}</div>
                <el-rate v-model="skill.rating" disabled show-score />
                <div class="rating-count">{{ skill.rating_count }} 人评分</div>
              </div>
              <el-divider />
              <div class="user-rating">
                <h4>我的评分</h4>
                <div v-if="skill.user_rating">
                  <el-rate v-model="skill.user_rating" disabled />
                  <span>{{ skill.user_rating }} 分</span>
                </div>
                <div v-else>
                  <el-rate v-model="myRating" @change="handleRate" />
                  <span>点击星星评分</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <!-- 操作面板 -->
          <el-card class="action-card">
            <template #header>
              <h3>操作</h3>
            </template>
            <div class="actions">
              <el-button
                v-if="skill.is_saved"
                type="warning"
                :icon="StarFilled"
                @click="handleUnsave"
              >
                已收藏
              </el-button>
              <el-button v-else :icon="Star" @click="handleSave">
                收藏
              </el-button>

              <el-button type="primary" :icon="VideoPlay" @click="handleTry">
                立即试用
              </el-button>

              <el-button type="success" :icon="Plus" @click="showCreateAgentDialog = true">
                创建代理
              </el-button>
            </div>
          </el-card>

          <!-- 统计信息 -->
          <el-card class="stats-card">
            <template #header>
              <h3>统计信息</h3>
            </template>
            <div class="stats">
              <div class="stat-item">
                <el-icon><View /></el-icon>
                <span>使用 {{ skill.usage_count }} 次</span>
              </div>
              <div class="stat-item">
                <el-icon><Star /></el-icon>
                <span>{{ skill.rating_count }} 人评分</span>
              </div>
              <div v-if="skill.rating" class="stat-item">
                <el-icon><TrendCharts /></el-icon>
                <span>平均 {{ skill.rating }} 分</span>
              </div>
            </div>
          </el-card>

          <!-- 技能元数据 -->
          <el-card v-if="skill.meta" class="meta-card">
            <template #header>
              <h3>技能元数据</h3>
            </template>
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item
                v-for="(value, key) in skill.meta"
                :key="key"
                :label="key"
              >
                {{ value }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 试用对话框 -->
    <el-dialog v-model="showTryDialog" title="试用技能" width="700px">
      <el-form label-width="80px">
        <el-form-item label="消息">
          <el-input
            v-model="tryMessage"
            type="textarea"
            :rows="4"
            placeholder="请输入要发送给技能的消息"
            :disabled="trying"
          />
        </el-form-item>
      </el-form>

      <div v-if="marketplaceStore.tryResult" class="try-result">
        <h4>试用结果</h4>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="状态">
            <el-tag :type="marketplaceStore.tryResult.status === 'success' ? 'success' : 'danger'">
              {{ marketplaceStore.tryResult.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行时间">
            {{ marketplaceStore.tryResult.execution_time?.toFixed(2) }}秒
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="marketplaceStore.tryResult.output_message" class="result-content">
          <h5>输出:</h5>
          <pre>{{ marketplaceStore.tryResult.output_message }}</pre>
        </div>

        <div v-if="marketplaceStore.tryResult.error_message" class="error-content">
          <h5>错误:</h5>
          <pre>{{ marketplaceStore.tryResult.error_message }}</pre>
        </div>
      </div>

      <template #footer>
        <el-button @click="showTryDialog = false" :disabled="trying">关闭</el-button>
        <el-button
          type="primary"
          :loading="trying"
          @click="handleExecuteTry"
          :disabled="!tryMessage.trim()"
        >
          执行
        </el-button>
      </template>
    </el-dialog>

    <!-- 创建代理对话框 -->
    <el-dialog v-model="showCreateAgentDialog" title="从技能创建代理" width="600px">
      <el-form :model="agentForm" :rules="agentRules" ref="agentFormRef" label-width="100px">
        <el-form-item label="代理名称" prop="agent_name">
          <el-input v-model="agentForm.agent_name" placeholder="请输入代理名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="agentForm.description" type="textarea" :rows="3" placeholder="请输入代理描述" />
        </el-form-item>
        <el-form-item label="模型">
          <el-select v-model="agentForm.model_name" placeholder="请选择模型">
            <el-option label="Qwen Max" value="qwen-max" />
            <el-option label="Qwen Plus" value="qwen-plus" />
            <el-option label="Qwen Turbo" value="qwen-turbo" />
            <el-option label="DeepSeek Chat" value="deepseek-chat" />
            <el-option label="DeepSeek Coder" value="deepseek-coder" />
          </el-select>
        </el-form-item>
        <el-form-item label="温度">
          <el-slider v-model="agentForm.temperature" :min="0" :max="2" :step="0.1" show-input />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateAgentDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreateAgent">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMarketplaceStore } from '@/stores'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import {
  ArrowLeft,
  Star,
  StarFilled,
  VideoPlay,
  Plus,
  View,
  TrendCharts,
} from '@element-plus/icons-vue'
import type { CreateAgentFromSkillRequest } from '@/api/marketplace'

const router = useRouter()
const route = useRoute()
const marketplaceStore = useMarketplaceStore()

const showTryDialog = ref(false)
const showCreateAgentDialog = ref(false)
const tryMessage = ref('')
const trying = ref(false)
const creating = ref(false)
const myRating = ref(0)

const agentFormRef = ref<FormInstance>()
const agentForm = reactive<CreateAgentFromSkillRequest>({
  agent_name: '',
  description: '',
  model_name: 'qwen-max',
  temperature: 0.7,
})

const agentRules: FormRules = {
  agent_name: [{ required: true, message: '请输入代理名称', trigger: 'blur' }],
}

const skill = marketplaceStore.currentSkill!

// 返回
const goBack = () => {
  router.back()
}

// 收藏技能
const handleSave = async () => {
  try {
    await marketplaceStore.saveMarketplaceSkill(skill.id)
    ElMessage.success('收藏成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '收藏失败')
  }
}

// 取消收藏
const handleUnsave = async () => {
  try {
    await marketplaceStore.unsaveMarketplaceSkill(skill.id)
    ElMessage.success('已取消收藏')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// 试用技能
const handleTry = () => {
  tryMessage.value = ''
  marketplaceStore.clearTryResult()
  showTryDialog.value = true
}

// 执行试用
const handleExecuteTry = async () => {
  if (!tryMessage.value.trim()) {
    ElMessage.warning('请输入试用消息')
    return
  }

  trying.value = true
  try {
    await marketplaceStore.tryMarketplaceSkill(skill.id, {
      message: tryMessage.value,
    })

    if (marketplaceStore.tryResult?.status === 'success') {
      ElMessage.success('试用成功')
    } else {
      ElMessage.error('试用失败: ' + (marketplaceStore.tryResult?.error_message || '未知错误'))
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '试用失败')
  } finally {
    trying.value = false
  }
}

// 评分
const handleRate = async () => {
  if (myRating.value === 0) {
    ElMessage.warning('请选择评分')
    return
  }

  try {
    await marketplaceStore.rateMarketplaceSkill(skill.id, {
      rating: myRating.value,
    })
    ElMessage.success('评分成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '评分失败')
  }
}

// 创建代理
const handleCreateAgent = async () => {
  if (!agentFormRef.value) return

  await agentFormRef.value.validate(async (valid) => {
    if (valid) {
      creating.value = true
      try {
        const agent = await marketplaceStore.createAgentFromSkill(skill.id, agentForm)
        ElMessage.success('代理创建成功')
        showCreateAgentDialog.value = false
        // 跳转到代理详情页
        router.push({ name: 'AgentDetail', params: { id: agent.id } })
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '创建失败')
      } finally {
        creating.value = false
      }
    }
  })
}

onMounted(() => {
  const id = Number(route.params.id)
  marketplaceStore.fetchMarketplaceSkill(id)
})
</script>

<style scoped>
.skill-detail-view {
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  margin-bottom: 20px;
}

.title-section {
  margin-top: 16px;
}

.title-section .tags {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.title-section h1 {
  margin: 0 0 12px 0;
  color: #303133;
}

.title-section .meta {
  color: #909399;
  font-size: 14px;
}

.title-section .meta span {
  margin-right: 20px;
}

.detail-card {
  margin-bottom: 20px;
}

.detail-card h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.description {
  color: #606266;
  line-height: 1.8;
}

.skill-content {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
}

.documentation {
  color: #606266;
  line-height: 1.8;
}

.action-card,
.stats-card,
.meta-card {
  margin-bottom: 20px;
}

.action-card h3,
.stats-card h3,
.meta-card h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.actions .el-button {
  width: 100%;
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.rating-section {
  padding: 16px 0;
}

.average-rating {
  text-align: center;
  margin-bottom: 24px;
}

.rating-number {
  font-size: 48px;
  font-weight: bold;
  color: #f59e0b;
  margin-bottom: 8px;
}

.rating-count {
  color: #909399;
  font-size: 14px;
  margin-top: 8px;
}

.user-rating {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-rating h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.try-result {
  margin-top: 20px;
}

.try-result h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.try-result h5 {
  margin: 10px 0 5px 0;
  color: #606266;
  font-size: 14px;
}

.result-content pre,
.error-content pre {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
}

.error-content pre {
  background-color: #fef0f0;
  color: #f56c6c;
}
</style>
