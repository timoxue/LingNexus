<template>
  <div class="agents-view">
    <div class="header">
      <h1>代理管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建代理
      </el-button>
    </div>

    <!-- 代理列表 -->
    <el-card class="table-card">
      <el-table v-loading="agentsStore.loading" :data="agentsStore.agents" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="model_name" label="模型" width="150" />
        <el-table-column prop="temperature" label="温度" width="100" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewAgent(row)">查看</el-button>
            <el-button link type="primary" @click="editAgent(row)">编辑</el-button>
            <el-button link type="warning" @click="executeAgent(row)">执行</el-button>
            <el-button link type="danger" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingAgent ? '编辑代理' : '创建代理'"
      width="700px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入代理名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入代理描述" />
        </el-form-item>
        <el-form-item label="模型" prop="model_name">
          <el-select v-model="form.model_name" placeholder="请选择模型">
            <el-option label="Qwen Max" value="qwen-max" />
            <el-option label="Qwen Plus" value="qwen-plus" />
            <el-option label="Qwen Turbo" value="qwen-turbo" />
            <el-option label="DeepSeek Chat" value="deepseek-chat" />
            <el-option label="DeepSeek Coder" value="deepseek-coder" />
          </el-select>
        </el-form-item>
        <el-form-item label="温度" prop="temperature">
          <el-slider v-model="form.temperature" :min="0" :max="2" :step="0.1" show-input />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="agentsStore.loading" @click="handleSubmit">
          {{ editingAgent ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAgentsStore } from '@/stores'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { Agent, AgentCreate } from '@/api/agents'

const router = useRouter()
const agentsStore = useAgentsStore()

const formRef = ref<FormInstance>()
const showCreateDialog = ref(false)
const editingAgent = ref<Agent | null>(null)

// 表单数据
const form = reactive({
  name: '',
  description: '',
  model_name: 'qwen-max',
  temperature: 0.7,
})

// 表单验证规则
const rules: FormRules = {
  name: [{ required: true, message: '请输入代理名称', trigger: 'blur' }],
  model_name: [{ required: true, message: '请选择模型', trigger: 'change' }],
}

// 格式化日期
const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

// 获取数据
const fetchData = () => {
  agentsStore.fetchAgents()
}

// 查看代理
const viewAgent = (agent: Agent) => {
  router.push({ name: 'AgentDetail', params: { id: agent.id } })
}

// 编辑代理
const editAgent = (agent: Agent) => {
  editingAgent.value = agent
  form.name = agent.name
  form.description = agent.description || ''
  form.model_name = agent.model_name
  form.temperature = agent.temperature
  showCreateDialog.value = true
}

// 执行代理
const executeAgent = (agent: Agent) => {
  ElMessage.info('执行功能待实现')
}

// 确认删除
const confirmDelete = (agent: Agent) => {
  ElMessageBox.confirm(`确定要删除代理 "${agent.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await agentsStore.deleteAgent(agent.id)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}

// 处理提交
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const data: AgentCreate = {
          name: form.name,
          description: form.description,
          model_name: form.model_name,
          temperature: form.temperature,
        }

        if (editingAgent.value) {
          await agentsStore.updateAgent(editingAgent.value.id, data)
          ElMessage.success('更新成功')
        } else {
          await agentsStore.createAgent(data)
          ElMessage.success('创建成功')
        }

        showCreateDialog.value = false
        editingAgent.value = null
        resetForm()
        fetchData()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
      }
    }
  })
}

// 重置表单
const resetForm = () => {
  form.name = ''
  form.description = ''
  form.model_name = 'qwen-max'
  form.temperature = 0.7
  formRef.value?.resetFields()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.agents-view {
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

.table-card {
  margin-bottom: 20px;
}
</style>
