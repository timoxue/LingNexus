<!--
技能同步按钮组件
用于从 Framework 自动同步技能到 Platform
-->
<template>
  <div class="skill-sync-container">
    <el-dropdown split-button type="primary" @click="handleSync(false)" @command="handleCommand">
      <el-icon v-if="loading" class="is-loading"><Loading /></el-icon>
      <el-icon v-else><Refresh /></el-icon>
      {{ loading ? '同步中...' : '同步技能' }}

      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="sync">
            <el-icon><Refresh /></el-icon>
            仅同步新技能
          </el-dropdown-item>
          <el-dropdown-item command="force">
            <el-icon><RefreshRight /></el-icon>
            强制更新所有技能
          </el-dropdown-item>
          <el-dropdown-item command="status" divided>
            <el-icon><InfoFilled /></el-icon>
            查看同步状态
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <!-- 同步结果对话框 -->
    <el-dialog
      v-model="resultDialogVisible"
      title="同步结果"
      width="500px"
      :close-on-click-modal="false"
    >
      <div v-if="syncResult">
        <el-alert
          :type="syncResult.failed > 0 ? 'warning' : 'success'"
          :closable="false"
          show-icon
        >
          <template #title>
            {{ syncResult.message }}
          </template>
        </el-alert>

        <el-descriptions :column="2" border class="sync-statistics">
          <el-descriptions-item label="总计">{{ syncResult.total }}</el-descriptions-item>
          <el-descriptions-item label="已创建">
            <el-tag type="success">{{ syncResult.created }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="已更新">
            <el-tag type="primary">{{ syncResult.updated }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="已跳过">
            <el-tag type="info">{{ syncResult.skipped }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="失败" :span="2">
            <el-tag v-if="syncResult.failed > 0" type="danger">{{ syncResult.failed }}</el-tag>
            <el-tag v-else type="success">0</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 错误列表 -->
        <div v-if="syncResult.errors.length > 0" class="error-list">
          <el-divider content-position="left">错误详情</el-divider>
          <el-scrollbar max-height="200px">
            <ul>
              <li v-for="(error, index) in syncResult.errors" :key="index">
                {{ error }}
              </li>
            </ul>
          </el-scrollbar>
        </div>
      </div>

      <template #footer>
        <el-button @click="resultDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="refreshSkills">刷新列表</el-button>
      </template>
    </el-dialog>

    <!-- 同步状态对话框 -->
    <el-dialog
      v-model="statusDialogVisible"
      title="同步状态"
      width="500px"
    >
      <div v-if="syncStatus">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Framework 路径">
            <el-text truncated>{{ syncStatus.framework_path }}</el-text>
          </el-descriptions-item>
          <el-descriptions-item label="技能目录存在">
            <el-tag :type="syncStatus.skills_dir_exists ? 'success' : 'danger'">
              {{ syncStatus.skills_dir_exists ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="External 技能数量">
            <el-tag type="primary">{{ syncStatus.external_skills_count }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Internal 技能数量">
            <el-tag type="success">{{ syncStatus.internal_skills_count }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总计">
            <el-tag type="info">{{ syncStatus.total_skills_count }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="statusDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleSync">立即同步</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, Refresh, RefreshRight, InfoFilled } from '@element-plus/icons-vue'
import { syncSkills, getSyncStatus, type SkillSyncResult, type SkillSyncStatus } from '@/api/skills'

interface Props {
  onSuccess?: () => void
}

const props = defineProps<Props>()

const loading = ref(false)
const resultDialogVisible = ref(false)
const statusDialogVisible = ref(false)
const syncResult = ref<SkillSyncResult | null>(null)
const syncStatus = ref<SkillSyncStatus | null>(null)

const handleSync = async (forceUpdate = false) => {
  if (loading.value) return

  try {
    await ElMessageBox.confirm(
      forceUpdate
        ? '确定要强制更新所有技能吗？这将覆盖现有技能的内容。'
        : '确定要同步技能吗？这将仅导入新技能。',
      '确认同步',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  loading.value = true

  try {
    const result = await syncSkills(forceUpdate)
    syncResult.value = result
    resultDialogVisible.value = true

    // 显示成功消息
    if (result.failed === 0) {
      ElMessage.success(result.message)
    } else {
      ElMessage.warning(`同步完成，但有 ${result.failed} 个失败`)
    }

    // 触发成功回调
    if (props.onSuccess) {
      props.onSuccess()
    }
  } catch (error: any) {
    const message = error.response?.data?.detail || '同步失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

const handleCommand = (command: string) => {
  switch (command) {
    case 'sync':
      handleSync(false)
      break
    case 'force':
      handleSync(true)
      break
    case 'status':
      showStatus()
      break
  }
}

const showStatus = async () => {
  try {
    const status = await getSyncStatus()
    syncStatus.value = status
    statusDialogVisible.value = true
  } catch (error: any) {
    const message = error.response?.data?.detail || '获取状态失败'
    ElMessage.error(message)
  }
}

const refreshSkills = () => {
  resultDialogVisible.value = false
  if (props.onSuccess) {
    props.onSuccess()
  }
}
</script>

<style scoped>
.skill-sync-container {
  display: inline-block;
}

.sync-statistics {
  margin-top: 20px;
}

.error-list {
  margin-top: 20px;
}

.error-list ul {
  padding-left: 20px;
  margin: 0;
}

.error-list li {
  color: #f56c6c;
  margin-bottom: 8px;
}

.el-icon {
  margin-right: 5px;
}

.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
