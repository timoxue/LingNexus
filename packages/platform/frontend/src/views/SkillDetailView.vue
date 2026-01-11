<template>
  <div class="skill-detail-view">
    <el-page-header @back="$router.back()" title="返回" content="技能详情" />
    <el-card class="detail-card" v-loading="skillsStore.loading">
      <template v-if="skillsStore.currentSkill">
        <h1>{{ skillsStore.currentSkill.name }}</h1>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ skillsStore.currentSkill.id }}</el-descriptions-item>
          <el-descriptions-item label="类别">
            <el-tag :type="skillsStore.currentSkill.category === 'external' ? 'primary' : 'success'">
              {{ skillsStore.currentSkill.category === 'external' ? '外部技能' : '内部技能' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="版本">{{ skillsStore.currentSkill.version }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="skillsStore.currentSkill.is_active ? 'success' : 'info'">
              {{ skillsStore.currentSkill.is_active ? '启用' : '禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(skillsStore.currentSkill.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(skillsStore.currentSkill.updated_at) }}</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <h2>技能内容</h2>
        <pre class="skill-content">{{ skillsStore.currentSkill.content }}</pre>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useSkillsStore } from '@/stores'

const route = useRoute()
const skillsStore = useSkillsStore()

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  const id = Number(route.params.id)
  skillsStore.fetchSkill(id)
})
</script>

<style scoped>
.skill-detail-view {
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

.skill-content {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
