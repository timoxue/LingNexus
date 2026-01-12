<template>
  <div class="marketplace-view">
    <div class="header">
      <h1>技能市场</h1>
      <el-space>
        <el-button type="primary" @click="showMySkillsDialog = true">
          <el-icon><Collection /></el-icon>
          我的收藏
        </el-button>
      </el-space>
    </div>

    <!-- 搜索和过滤 -->
    <el-card class="filter-card">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-input
            v-model="searchQuery"
            placeholder="搜索技能..."
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.category" placeholder="类别" clearable @change="handleFilter">
            <el-option label="外部技能" value="external" />
            <el-option label="内部技能" value="internal" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.sort_by" placeholder="排序" @change="handleFilter">
            <el-option label="最新创建" value="created_at" />
            <el-option label="评分最高" value="rating" />
            <el-option label="使用最多" value="usage_count" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.sharing_scope" placeholder="共享范围" clearable @change="handleFilter">
            <el-option label="公开" value="public" />
            <el-option label="团队" value="team" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-checkbox v-model="filters.is_official" @change="handleFilter" border>
            只看官方
          </el-checkbox>
        </el-col>
      </el-row>
    </el-card>

    <!-- 技能列表 -->
    <div v-loading="marketplaceStore.loading" class="skills-grid">
      <el-card
        v-for="skill in marketplaceStore.skills"
        :key="skill.id"
        class="skill-card"
        shadow="hover"
      >
        <template #header>
          <div class="skill-card-header">
            <div class="skill-title">
              <el-tag v-if="skill.is_official" type="success" size="small" effect="dark">
                官方
              </el-tag>
              <el-tag :type="skill.category === 'external' ? 'primary' : 'warning'" size="small">
                {{ skill.category === 'external' ? '外部' : '内部' }}
              </el-tag>
              <span class="name">{{ skill.name }}</span>
            </div>
            <div class="skill-actions">
              <el-button
                v-if="skill.is_saved"
                type="warning"
                :icon="StarFilled"
                circle
                size="small"
                @click="handleUnsave(skill)"
              />
              <el-button
                v-else
                :icon="Star"
                circle
                size="small"
                @click="handleSave(skill)"
              />
            </div>
          </div>
        </template>

        <div class="skill-content">
          <div class="skill-description">
            {{ skill.meta?.description || skill.content?.substring(0, 100) + '...' }}
          </div>

          <div class="skill-meta">
            <div class="meta-item">
              <el-icon><User /></el-icon>
              <span>{{ skill.creator_name || '未知' }}</span>
            </div>
            <div class="meta-item">
              <el-icon><View /></el-icon>
              <span>{{ skill.usage_count }} 次使用</span>
            </div>
            <div v-if="skill.rating" class="meta-item">
              <el-rate
                v-model="skill.rating"
                disabled
                show-score
                score-template="{value}"
                size="small"
              />
            </div>
          </div>

          <el-tag v-if="skill.sharing_scope === 'public'" type="success" size="small" plain>
            公开
          </el-tag>
          <el-tag v-else-if="skill.sharing_scope === 'team'" type="info" size="small" plain>
            团队
          </el-tag>
          <el-tag v-else type="warning" size="small" plain>
            私有
          </el-tag>
        </div>

        <template #footer>
          <el-button type="primary" link @click="viewSkill(skill)">
            查看详情
          </el-button>
          <el-button type="success" link @click="handleTry(skill)">
            立即试用
          </el-button>
          <el-button type="warning" link @click="handleCreateAgent(skill)">
            创建 Agent
          </el-button>
        </template>
      </el-card>
    </div>

    <!-- 试用对话框 -->
    <el-dialog v-model="showTryDialog" title="试用技能" width="700px">
      <div v-if="selectedSkill">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="技能名称">{{ selectedSkill.name }}</el-descriptions-item>
          <el-descriptions-item label="类别">
            {{ selectedSkill.category === 'external' ? '外部' : '内部' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

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

        <el-divider v-if="marketplaceStore.tryResult" />

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

    <!-- 我的收藏对话框 -->
    <el-dialog v-model="showMySkillsDialog" title="我的收藏" width="900px">
      <div v-loading="marketplaceStore.loading">
        <el-table :data="marketplaceStore.savedSkills" stripe>
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="category" label="类别" width="100">
            <template #default="{ row }">
              <el-tag :type="row.category === 'external' ? 'primary' : 'warning'" size="small">
                {{ row.category === 'external' ? '外部' : '内部' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="usage_count" label="使用次数" width="100" />
          <el-table-column label="评分" width="120">
            <template #default="{ row }">
              <el-rate v-model="row.rating" disabled size="small" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button link type="primary" @click="viewSkill(row)">查看</el-button>
              <el-button link type="success" @click="handleTry(row)">试用</el-button>
              <el-button link type="danger" @click="handleUnsave(row)">取消收藏</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 创建 Agent 对话框 -->
    <el-dialog v-model="showCreateAgentDialog" title="创建 Agent" width="600px">
      <div v-if="selectedSkillForAgent">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="技能名称">{{ selectedSkillForAgent.name }}</el-descriptions-item>
          <el-descriptions-item label="类别">
            {{ selectedSkillForAgent.category === 'external' ? '外部' : '内部' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <el-form :model="agentForm" :rules="agentFormRules" ref="agentFormRef" label-width="100px">
          <el-form-item label="Agent 名称" prop="name">
            <el-input v-model="agentForm.name" placeholder="请输入 Agent 名称" />
            <div class="form-tip">建议使用描述性名称，如 "文档生成助手"</div>
          </el-form-item>
          <el-form-item label="描述" prop="description">
            <el-input v-model="agentForm.description" type="textarea" :rows="3" placeholder="请输入 Agent 描述" />
          </el-form-item>
          <el-form-item label="模型" prop="model_name">
            <el-select v-model="agentForm.model_name" placeholder="请选择模型">
              <el-option label="Qwen Max" value="qwen-max" />
              <el-option label="Qwen Plus" value="qwen-plus" />
              <el-option label="Qwen Turbo" value="qwen-turbo" />
              <el-option label="DeepSeek Chat" value="deepseek-chat" />
              <el-option label="DeepSeek Coder" value="deepseek-coder" />
            </el-select>
          </el-form-item>
          <el-form-item label="温度" prop="temperature">
            <el-slider v-model="agentForm.temperature" :min="0" :max="2" :step="0.1" show-input />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="showCreateAgentDialog = false">取消</el-button>
        <el-button type="primary" :loading="creatingAgent" @click="handleCreateAgentSubmit">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMarketplaceStore, useAgentsStore } from '@/stores'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  Search,
  Collection,
  Star,
  StarFilled,
  User,
  View,
} from '@element-plus/icons-vue'
import type { MarketplaceSkill } from '@/api/marketplace'
import type { AgentCreate } from '@/api/agents'

const router = useRouter()
const marketplaceStore = useMarketplaceStore()
const agentsStore = useAgentsStore()

const searchQuery = ref('')
const filters = reactive({
  category: undefined as string | undefined,
  sort_by: 'created_at',
  sharing_scope: undefined as string | undefined,
  is_official: undefined as boolean | undefined,
})

const showTryDialog = ref(false)
const showMySkillsDialog = ref(false)
const showCreateAgentDialog = ref(false)
const selectedSkill = ref<MarketplaceSkill | null>(null)
const selectedSkillForAgent = ref<MarketplaceSkill | null>(null)
const tryMessage = ref('')
const trying = ref(false)
const creatingAgent = ref(false)
const agentFormRef = ref<FormInstance>()

// Agent 创建表单
const agentForm = reactive({
  name: '',
  description: '',
  model_name: 'qwen-max',
  temperature: 0.7,
})

const agentFormRules: FormRules = {
  name: [{ required: true, message: '请输入 Agent 名称', trigger: 'blur' }],
  model_name: [{ required: true, message: '请选择模型', trigger: 'change' }],
}

// 获取数据
const fetchData = () => {
  marketplaceStore.fetchMarketplaceSkills({
    search: searchQuery.value || undefined,
    category: filters.category as any,
    sort_by: filters.sort_by as any,
    sharing_scope: filters.sharing_scope as any,
    is_official: filters.is_official,
  })
}

// 搜索
const handleSearch = () => {
  fetchData()
}

// 过滤
const handleFilter = () => {
  fetchData()
}

// 查看技能详情
const viewSkill = (skill: MarketplaceSkill) => {
  router.push({ name: 'MarketplaceSkillDetail', params: { id: skill.id } })
}

// 试用技能
const handleTry = (skill: MarketplaceSkill) => {
  selectedSkill.value = skill
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
    await marketplaceStore.tryMarketplaceSkill(selectedSkill.value!.id, {
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

// 收藏技能
const handleSave = async (skill: MarketplaceSkill) => {
  try {
    await marketplaceStore.saveMarketplaceSkill(skill.id)
    ElMessage.success('收藏成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '收藏失败')
  }
}

// 取消收藏
const handleUnsave = async (skill: MarketplaceSkill) => {
  try {
    await marketplaceStore.unsaveMarketplaceSkill(skill.id)
    ElMessage.success('已取消收藏')
    // 如果在收藏列表中，刷新数据
    if (showMySkillsDialog.value) {
      marketplaceStore.fetchSavedSkills()
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// 创建 Agent
const handleCreateAgent = (skill: MarketplaceSkill) => {
  selectedSkillForAgent.value = skill
  agentForm.name = `${skill.name}助手`
  agentForm.description = `使用 ${skill.name} 技能的 AI 助手`
  agentForm.model_name = 'qwen-max'
  agentForm.temperature = 0.7
  showCreateAgentDialog.value = true
}

// 提交创建 Agent
const handleCreateAgentSubmit = async () => {
  if (!agentFormRef.value) return

  await agentFormRef.value.validate(async (valid) => {
    if (valid && selectedSkillForAgent.value) {
      creatingAgent.value = true
      try {
        const data: AgentCreate = {
          name: agentForm.name,
          description: agentForm.description,
          model_name: agentForm.model_name,
          temperature: agentForm.temperature,
          skill_ids: [selectedSkillForAgent.value.id],
        }

        await agentsStore.createAgent(data)
        ElMessage.success('Agent 创建成功')
        showCreateAgentDialog.value = false

        // 跳转到 Agent 列表
        router.push({ name: 'Agents' })
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '创建失败')
      } finally {
        creatingAgent.value = false
      }
    }
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.marketplace-view {
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

.filter-card {
  margin-bottom: 20px;
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.skill-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.skill-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.skill-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.skill-title .name {
  font-weight: 600;
  color: #303133;
}

.skill-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skill-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  min-height: 60px;
}

.skill-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 13px;
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

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.5;
}
</style>
