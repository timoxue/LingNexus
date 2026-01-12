<template>
  <div class="skills-view">
    <div class="header">
      <h1>技能管理</h1>
      <el-space>
        <!-- 同步技能按钮（仅管理员可见） -->
        <SkillSyncButton v-if="userStore.is_superuser" @success="fetchData" />
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          创建技能
        </el-button>
      </el-space>
    </div>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="类别">
          <el-select v-model="filters.category" placeholder="全部" clearable @change="fetchData">
            <el-option label="外部技能" value="external" />
            <el-option label="内部技能" value="internal" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.is_active" placeholder="全部" clearable @change="fetchData">
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 技能列表 -->
    <el-card class="table-card">
      <el-table v-loading="skillsStore.loading" :data="skillsStore.skills" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="category" label="类别" width="120">
          <template #default="{ row }">
            <el-tag :type="row.category === 'external' ? 'primary' : 'success'">
              {{ row.category === 'external' ? '外部技能' : '内部技能' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="100" />
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
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewSkill(row)">查看</el-button>
            <el-button link type="primary" @click="editSkill(row)">编辑</el-button>
            <el-button link type="danger" @click="confirmDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingSkill ? '编辑技能' : '创建技能'"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入技能名称" />
        </el-form-item>
        <el-form-item label="类别" prop="category">
          <el-select v-model="form.category" placeholder="请选择类别">
            <el-option label="外部技能" value="external" />
            <el-option label="内部技能" value="internal" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="10"
            placeholder="请输入技能内容 (SKILL.md 格式)"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="skillsStore.loading" @click="handleSubmit">
          {{ editingSkill ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSkillsStore, useUserStore } from '@/stores'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import type { Skill, SkillCreate, SkillUpdate } from '@/api/skills'
import SkillSyncButton from '@/components/SkillSyncButton.vue'

const router = useRouter()
const skillsStore = useSkillsStore()
const userStore = useUserStore()

const formRef = ref<FormInstance>()
const showCreateDialog = ref(false)
const editingSkill = ref<Skill | null>(null)

// 筛选条件
const filters = reactive({
  category: undefined as 'external' | 'internal' | undefined,
  is_active: undefined as boolean | undefined,
})

// 表单数据
const form = reactive({
  name: '',
  category: 'external' as 'external' | 'internal',
  content: '',
})

// 表单验证规则
const rules: FormRules = {
  name: [{ required: true, message: '请输入技能名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择类别', trigger: 'change' }],
  content: [{ required: true, message: '请输入技能内容', trigger: 'blur' }],
}

// 格式化日期
const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

// 获取数据
const fetchData = () => {
  skillsStore.fetchSkills(filters)
}

// 查看技能
const viewSkill = (skill: Skill) => {
  router.push({ name: 'SkillDetail', params: { id: skill.id } })
}

// 编辑技能
const editSkill = (skill: Skill) => {
  editingSkill.value = skill
  form.name = skill.name
  form.category = skill.category
  form.content = skill.content
  showCreateDialog.value = true
}

// 确认删除
const confirmDelete = (skill: Skill) => {
  ElMessageBox.confirm(`确定要删除技能 "${skill.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await skillsStore.deleteSkill(skill.id)
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
        const data: SkillCreate = {
          name: form.name,
          category: form.category,
          content: form.content,
        }

        if (editingSkill.value) {
          await skillsStore.updateSkill(editingSkill.value.id, data)
          ElMessage.success('更新成功')
        } else {
          await skillsStore.createSkill(data)
          ElMessage.success('创建成功')
        }

        showCreateDialog.value = false
        editingSkill.value = null
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
  form.category = 'external'
  form.content = ''
  formRef.value?.resetFields()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.skills-view {
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

.table-card {
  margin-bottom: 20px;
}
</style>
