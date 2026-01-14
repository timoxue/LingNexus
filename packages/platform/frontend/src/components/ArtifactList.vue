<template>
  <div v-if="artifacts && artifacts.length > 0" class="artifact-list">
    <div class="artifact-list-header">
      <el-icon><Document /></el-icon>
      <span>生成的文件 ({{ artifacts.length }})</span>
    </div>

    <el-table :data="artifacts" style="width: 100%" size="small">
      <el-table-column label="文件名" min-width="200">
        <template #default="{ row }">
          <div class="file-name">
            <el-icon class="file-icon">
              <component :is="getFileIcon(row.file_type)" />
            </el-icon>
            <span>{{ row.filename }}</span>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="类型" width="80">
        <template #default="{ row }">
          <el-tag size="small" :type="getFileTypeColor(row.file_type)">
            {{ row.file_type.toUpperCase() }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="大小" width="100">
        <template #default="{ row }">
          {{ formatFileSize(row.file_size) }}
        </template>
      </el-table-column>

      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            link
            @click="downloadFile(row)"
            :loading="downloading === row.file_id"
          >
            <el-icon><Download /></el-icon>
            下载
          </el-button>

          <el-button
            v-if="canPreview(row.file_type)"
            type="info"
            size="small"
            link
            @click="previewFile(row)"
            :loading="previewing === row.file_id"
          >
            <el-icon><View /></el-icon>
            预览
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      title="文件预览"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="previewingFile" class="preview-container">
        <!-- 图片预览 -->
        <el-image
          v-if="previewingFile.file_type === 'png' || previewingFile.file_type === 'jpg' || previewingFile.file_type === 'jpeg' || previewingFile.file_type === 'gif'"
          :src="getPreviewUrl(previewingFile.file_id)"
          fit="contain"
          style="width: 100%; max-height: 70vh"
        />

        <!-- PDF 预览 -->
        <iframe
          v-else-if="previewingFile.file_type === 'pdf'"
          :src="getPreviewUrl(previewingFile.file_id)"
          style="width: 100%; height: 70vh; border: none;"
        ></iframe>

        <!-- 文本预览 -->
        <pre
          v-else-if="previewingFile.file_type === 'txt' || previewingFile.file_type === 'md' || previewingFile.file_type === 'json'"
          class="text-preview"
        >{{ previewContent }}</pre>

        <!-- 其他文件类型 -->
        <el-alert
          v-else
          type="info"
          :closable="false"
          show-icon
        >
          此文件类型不支持在线预览，请下载后查看。
        </el-alert>
      </div>

      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
        <el-button
          v-if="previewingFile"
          type="primary"
          @click="downloadFile(previewingFile)"
          :loading="downloading === previewingFile?.file_id"
        >
          下载文件
        </el-button>
      </template>
    </el-dialog>
  </div>

  <el-empty
    v-else-if="showEmpty"
    description="暂无生成的文件"
    :image-size="100"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document,
  Download,
  View,
} from '@element-plus/icons-vue'
import type { AgentArtifact } from '@/api/files'
import {
  downloadAgentArtifact,
  getAgentArtifactDownloadUrl,
  getAgentArtifactPreviewUrl,
} from '@/api/files'

interface Props {
  artifacts: AgentArtifact[]
  showEmpty?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showEmpty: false,
})

const emit = defineEmits<{
  download: [artifact: AgentArtifact]
}>()

// 状态
const downloading = ref<string | null>(null)
const previewing = ref<string | null>(null)
const showPreviewDialog = ref(false)
const previewingFile = ref<AgentArtifact | null>(null)
const previewContent = ref('')

// 获取文件图标
const getFileIcon = (fileType: string) => {
  const iconMap: Record<string, any> = {
    docx: 'Document',
    pdf: 'Document',
    xlsx: 'Document',
    pptx: 'Document',
    png: 'Picture',
    jpg: 'Picture',
    jpeg: 'Picture',
    gif: 'Picture',
    txt: 'Document',
    md: 'Document',
    json: 'Document',
  }
  return iconMap[fileType] || 'Document'
}

// 获取文件类型颜色
const getFileTypeColor = (fileType: string) => {
  const colorMap: Record<string, string> = {
    docx: 'primary',
    pdf: 'danger',
    xlsx: 'success',
    pptx: 'warning',
    png: 'info',
    jpg: 'info',
    jpeg: 'info',
    gif: 'info',
    txt: 'info',
    md: 'info',
    json: 'info',
  }
  return colorMap[fileType] || 'info'
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`
}

// 判断是否可以预览
const canPreview = (fileType: string): boolean => {
  return ['png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'md', 'json'].includes(fileType)
}

// 获取预览 URL
const getPreviewUrl = (fileId: string): string => {
  return getAgentArtifactPreviewUrl(fileId)
}

// 下载文件
const downloadFile = async (artifact: AgentArtifact) => {
  downloading.value = artifact.file_id

  try {
    // 使用直接 URL 下载
    const url = getAgentArtifactDownloadUrl(artifact.file_id)
    const link = document.createElement('a')
    link.href = url
    link.download = artifact.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    ElMessage.success('文件下载成功')
    emit('download', artifact)
  } catch (error: any) {
    ElMessage.error(`文件下载失败: ${error.message || '未知错误'}`)
  } finally {
    downloading.value = null
  }
}

// 预览文件
const previewFile = async (artifact: AgentArtifact) => {
  previewing.value = artifact.file_id
  previewingFile.value = artifact

  // 如果是文本文件，先读取内容
  if (['txt', 'md', 'json'].includes(artifact.file_type)) {
    try {
      const url = getAgentArtifactPreviewUrl(artifact.file_id)
      const response = await fetch(url)
      const text = await response.text()
      previewContent.value = text
    } catch (error: any) {
      ElMessage.error(`预览失败: ${error.message || '未知错误'}`)
      previewing.value = null
      return
    }
  }

  showPreviewDialog.value = true
  previewing.value = null
}
</script>

<script lang="ts">
// 添加图片组件
import { Picture } from '@element-plus/icons-vue'

export default {
  components: {
    Picture,
  },
}
</script>

<style scoped>
.artifact-list {
  margin-top: 20px;
}

.artifact-list-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  font-size: 16px;
  color: #909399;
}

.preview-container {
  min-height: 300px;
}

.text-preview {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  max-height: 60vh;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
}
</style>
