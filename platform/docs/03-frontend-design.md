# 前端设计文档

## 技术栈

### 核心框架
- **Vue 3.4+** - 渐进式JavaScript框架
- **TypeScript 5.3+** - 类型安全
- **Vite 5.0+** - 构建工具

### UI 框架
- **Element Plus 2.5+** - UI 组件库
- **Tailwind CSS 3.4+** - 原子化 CSS (可选)

### 状态管理
- **Pinia 2.1+** - 状态管理
- **VueUse 10.7+** - 组合式工具集

### 路由
- **Vue Router 4.2+** - 官方路由

### 网络请求
- **Axios 1.6+** - HTTP 客户端
- **SSE / WebSocket** - 实时通信

### 可视化
- **React Flow 11.10+** - 流程图编辑器
- **ECharts 5.4+** - 数据可视化

### 代码质量
- **ESLint** - 代码检查
- **Prettier** - 代码格式化
- **TypeScript** - 类型检查

---

## 项目结构

```
platform/frontend/
├── public/                     # 静态资源
│   ├── favicon.ico
│   └── logo.png
│
├── src/
│   ├── api/                   # API 调用
│   │   ├── client.ts          # Axios 实例
│   │   ├── auth.ts            # 认证 API
│   │   ├── skills.ts          # Skill API
│   │   ├── agents.ts          # Agent API
│   │   └── types.ts           # API 类型定义
│   │
│   ├── assets/                # 资源文件
│   │   ├── styles/
│   │   │   ├── main.css       # 全局样式
│   │   │   └── variables.css  # CSS 变量
│   │   └── images/
│   │
│   ├── components/            # 通用组件
│   │   ├── common/
│   │   │   ├── Header.vue     # 头部导航
│   │   │   ├── Footer.vue     # 页脚
│   │   │   ├── Sidebar.vue    # 侧边栏
│   │   │   └── Loading.vue    # 加载组件
│   │   │
│   │   ├── skill/
│   │   │   ├── SkillCard.vue  # Skill 卡片
│   │   │   ├── SkillList.vue  # Skill 列表
│   │   │   └── SkillEditor.vue # Skill 编辑器
│   │   │
│   │   ├── agent/
│   │   │   ├── AgentCard.vue  # Agent 卡片
│   │   │   └── AgentBuilder.vue # Agent 构建器
│   │   │
│   │   └── ui/
│   │       ├── MarkdownEditor.vue # Markdown 编辑器
│   │       ├── CodeEditor.vue     # 代码编辑器
│   │       └── FileUpload.vue     # 文件上传
│   │
│   ├── views/                # 页面视图
│   │   ├── Home.vue           # 首页
│   │   ├── Auth/
│   │   │   ├── Login.vue      # 登录页
│   │   │   └── Register.vue   # 注册页
│   │   │
│   │   ├── Skills/
│   │   │   ├── SkillList.vue      # Skill 列表页
│   │   │   ├── SkillDetail.vue    # Skill 详情页
│   │   │   ├── SkillCreate.vue    # 创建 Skill 页
│   │   │   ├── SkillEdit.vue      # 编辑 Skill 页
│   │   │   └── SkillMarket.vue    # Skill 市场
│   │   │
│   │   ├── Agents/
│   │   │   ├── AgentList.vue      # Agent 列表页
│   │   │   ├── AgentDetail.vue    # Agent 详情页
│   │   │   └── AgentBuilder.vue   # 构建器页面
│   │   │
│   │   ├── Dashboard/
│   │   │   └── Overview.vue       # 仪表盘
│   │   │
│   │   └── Profile/
│   │       └── Settings.vue       # 用户设置
│   │
│   ├── stores/               # Pinia 状态管理
│   │   ├── auth.ts           # 认证状态
│   │   ├── skill.ts          # Skill 状态
│   │   ├── agent.ts          # Agent 状态
│   │   └── ui.ts             # UI 状态
│   │
│   ├── router/               # 路由配置
│   │   └── index.ts
│   │
│   ├── utils/                # 工具函数
│   │   ├── request.ts        # 请求封装
│   │   ├── format.ts         # 格式化工具
│   │   └── validate.ts       # 验证工具
│   │
│   ├── types/                # TypeScript 类型
│   │   ├── skill.ts
│   │   ├── agent.ts
│   │   └── user.ts
│   │
│   ├── App.vue               # 根组件
│   └── main.ts               # 入口文件
│
├── .env.development          # 开发环境变量
├── .env.production           # 生产环境变量
├── index.html                # HTML 模板
├── vite.config.ts            # Vite 配置
├── tsconfig.json             # TypeScript 配置
└── package.json              # 项目依赖
```

---

## 核心页面设计

### 1. Skill 编辑器 (SkillCreate.vue / SkillEdit.vue)

**布局**：
```
┌─────────────────────────────────────────────────────────────┐
│  Header: [保存] [预览] [发布] [取消]                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 📝 基本信息                                         │    │
│  ├────────────────────────────────────────────────────┤    │
│  │  Skill 名称: [____________________]                 │    │
│  │  描      述: [____________________]                 │    │
│  │  分      类: [法务 ▼]                               │    │
│  │  标      签: [+合同] [+风控] [x]                    │    │
│  │  可 见 性: (●) 私有  ○ 团队  ○ 公开                 │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 📄 Skill 内容 (SKILL.md)                           │    │
│  ├────────────────────────────────────────────────────┤    │
│  │  ┌──────────────────────────────────────────────┐  │    │
│  │  │ [Markdown 编辑器]                           │  │    │
│  │  │                                              │  │    │
│  │  │ # 合同审查助手                                │  │    │
│  │  │                                              │  │    │
│  │  │ ## 功能                                      │  │    │
│  │  │ ...                                          │  │    │
│  │  └──────────────────────────────────────────────┘  │    │
│  │  [切换预览] [切换源码]                             │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 📎 资源文件                                         │    │
│  ├────────────────────────────────────────────────────┤    │
│  │  [上传文件]                                          │    │
│  │  ✓ reference.pdf (2.3 MB)           [删除]         │    │
│  │  ✓ template.docx (125 KB)          [删除]         │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**核心功能**：
- 实时预览 Markdown 渲染
- 拖拽上传资源文件
- 自动保存 (每30秒)
- 版本历史对比
- 权限设置

### 2. Agent 构建器 (AgentBuilder.vue)

**布局**：
```
┌─────────────────────────────────────────────────────────────┐
│  Header: [保存] [运行] [设置]                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────────────────────────────┐ │
│  │              │  │  画布                                │ │
│  │  Skills      │  │                                      │ │
│  │  组件库       │  │  ┌──────┐    ┌──────┐    ┌──────┐  │ │
│  │              │  │  │Skill │───→│Skill │───→│Skill │  │ │
│  │ ┌──────────┐ │  │  │  A   │    │  B   │    │  C   │  │ │
│  │ │合同审查  │ │  │  └──────┘    └──────┘    └──────┘  │ │
│  │ │风险评估  │ │  │                                      │ │
│  │ │报告生成  │ │  │  [从左侧拖拽Skill到画布]              │ │
│  │ │...       │ │  │                                      │ │
│  │ └──────────┘ │  │                                      │ │
│  │              │  │                                      │ │
│  │  [添加Skill] │  └──────────────────────────────────────┘ │
│  └──────────────┘                                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ⚙️ 配置面板                                         │    │
│  ├────────────────────────────────────────────────────┤    │
│  │  Agent 名称: [合同处理工作流]                       │    │
│  │  模型选择: [qwen-max ▼]                            │    │
│  │  温度参数: [━━━━○○] 0.3                            │    │
│  │  记忆类型: (●) 长期 (7天)  ○ 短期  ○ 无            │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**核心功能**：
- 拖拽式编排
- 可视化连接线
- 实时配置面板
- 运行调试
- 导入/导出配置

### 3. Skill 市场 (SkillMarket.vue)

**布局**：
```
┌─────────────────────────────────────────────────────────────┐
│  🔍 [搜索 Skills...]          [分类 ▼] [排序 ▼] [筛选]     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │ 📄 合同审查 │  │ 📊 数据分析 │  │ 🔍 文档搜索 │           │
│  │            │  │            │  │            │           │
│  │ ⭐ 4.5     │  │ ⭐ 4.2     │  │ ⭐ 4.8     │           │
│  │ 👥 150使用  │  │ 👥 89使用   │  │ 👥 320使用   │           │
│  │            │  │            │  │            │           │
│  │ [详情]     │  │ [详情]     │  │ [详情]     │           │
│  │ [使用]     │  │ [使用]     │  │ [使用]     │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │ 📝 文档生成 │  │ 🔗 知识图谱 │  │ 🎨 设计助手 │           │
│  │ ...        │  │ ...        │  │ ...        │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│                                                              │
│  [< 上一页]  第 1 / 5 页  [下一页 >]                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**核心功能**：
- 搜索和筛选
- 分类浏览
- 评分和评论
- 一键使用/Fork
- 收藏功能

---

## 核心组件设计

### 1. SkillCard.vue

```vue
<template>
  <el-card class="skill-card" @click="goToDetail">
    <div class="skill-header">
      <el-icon class="skill-icon"><Document /></el-icon>
      <h3 class="skill-name">{{ skill.name }}</h3>
      <el-tag
        :type="visibilityType"
        size="small"
      >
        {{ visibilityText }}
      </el-tag>
    </div>

    <p class="skill-description">
      {{ skill.description }}
    </p>

    <div class="skill-meta">
      <el-rate
        v-model="skill.rating"
        disabled
        show-score
        text-color="#ff9900"
      />
      <span class="usage-count">
        <el-icon><User /></el-icon>
        {{ skill.usage_count }}
      </span>
    </div>

    <div class="skill-tags">
      <el-tag
        v-for="tag in skill.tags"
        :key="tag"
        size="small"
        type="info"
      >
        {{ tag }}
      </el-tag>
    </div>

    <div class="skill-actions">
      <el-button
        type="primary"
        size="small"
        @click.stop="useSkill"
      >
        使用
      </el-button>
      <el-button
        size="small"
        @click.stop="toggleFavorite"
      >
        <el-icon><Star /></el-icon>
      </el-button>
      <el-button
        size="small"
        @click.stop="forkSkill"
      >
        Fork
      </el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Skill } from '@/types/skill'

interface Props {
  skill: Skill
}

const props = defineProps<Props>()
const router = useRouter()

const visibilityType = computed(() => {
  const map = {
    private: 'danger',
    team: 'warning',
    public: 'success'
  }
  return map[props.skill.visibility] || 'info'
})

const visibilityText = computed(() => {
  const map = {
    private: '私有',
    team: '团队',
    public: '公开'
  }
  return map[props.skill.visibility] || '未知'
})

const goToDetail = () => {
  router.push(`/skills/${props.skill.id}`)
}

const useSkill = () => {
  // 跳转到 Agent 构建器并预选此 Skill
  router.push({
    path: '/agents/create',
    query: { skill_id: props.skill.id }
  })
}

const toggleFavorite = () => {
  // 切换收藏状态
}

const forkSkill = () => {
  // Fork Skill
}
</script>

<style scoped>
.skill-card {
  cursor: pointer;
  transition: all 0.3s;
}

.skill-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
```

### 2. AgentBuilder.vue (使用 React Flow)

```vue
<template>
  <div class="agent-builder">
    <div class="skills-panel">
      <h3>Skills 组件库</h3>
      <div
        v-for="skill in skills"
        :key="skill.id"
        class="skill-item"
        draggable
        @dragstart="onDragStart($event, skill)"
      >
        <el-icon><Document /></el-icon>
        <span>{{ skill.name }}</span>
      </div>
    </div>

    <div class="canvas-panel">
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        :default-viewport="{ zoom: 1.5 }"
        :min-zoom="0.2"
        :max-zoom="4"
        @drop="onDrop"
        @dragover="onDragOver"
      >
        <Background />
        <Controls />
        <MiniMap />
      </VueFlow>
    </div>

    <div class="config-panel">
      <h3>配置</h3>
      <el-form :model="agentConfig">
        <el-form-item label="Agent 名称">
          <el-input v-model="agentConfig.name" />
        </el-form-item>

        <el-form-item label="模型">
          <el-select v-model="agentConfig.model">
            <el-option label="Qwen Max" value="qwen-max" />
            <el-option label="Qwen Plus" value="qwen-plus" />
            <el-option label="DeepSeek" value="deepseek-chat" />
          </el-select>
        </el-form-item>

        <el-form-item label="温度">
          <el-slider v-model="agentConfig.temperature" :max="1" :step="0.1" />
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background, Controls, MiniMap } from '@vue-flow/addons'
import type { Skill } from '@/types/skill'

const { onConnect, addEdges } = useVueFlow()

const skills = ref<Skill[]>([])
const nodes = ref([])
const edges = ref([])

const agentConfig = ref({
  name: '',
  model: 'qwen-max',
  temperature: 0.3
})

const onDragStart = (event: DragEvent, skill: Skill) => {
  if (event.dataTransfer) {
    event.dataTransfer.setData('skill', JSON.stringify(skill))
  }
}

const onDrop = (event: DragEvent) => {
  const skillData = event.dataTransfer?.getData('skill')
  if (skillData) {
    const skill = JSON.parse(skillData)
    // 添加节点到画布
    nodes.value.push({
      id: `skill_${skill.id}`,
      type: 'custom',
      position: { x: event.offsetX, y: event.offsetY },
      data: { label: skill.name, skill }
    })
  }
}

const onDragOver = (event: DragEvent) => {
  event.preventDefault()
}

onConnect((params) => addEdges([params]))
</script>
```

---

## 状态管理 (Pinia)

### 1. auth.ts - 认证状态

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/user'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin ?? false)

  async function login(username: string, password: string) {
    const response = await authApi.login({ username, password })
    token.value = response.data.token
    user.value = response.data.user
    localStorage.setItem('token', response.data.token)
  }

  async function register(data: RegisterRequest) {
    const response = await authApi.register(data)
    token.value = response.data.token
    user.value = response.data.user
    localStorage.setItem('token', response.data.token)
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  async function fetchCurrentUser() {
    if (token.value) {
      const response = await authApi.getCurrentUser()
      user.value = response.data
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    isAdmin,
    login,
    register,
    logout,
    fetchCurrentUser
  }
})
```

### 2. skill.ts - Skill 状态

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Skill, SkillListFilters } from '@/types/skill'
import { skillApi } from '@/api/skills'

export const useSkillStore = defineStore('skill', () => {
  const skills = ref<Skill[]>([])
  const currentSkill = ref<Skill | null>(null)
  const loading = ref(false)
  const total = ref(0)

  async function fetchSkills(filters: SkillListFilters) {
    loading.value = true
    try {
      const response = await skillApi.list(filters)
      skills.value = response.data.items
      total.value = response.data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchSkillDetail(id: string) {
    loading.value = true
    try {
      const response = await skillApi.getDetail(id)
      currentSkill.value = response.data
    } finally {
      loading.value = false
    }
  }

  async function createSkill(data: CreateSkillRequest) {
    const response = await skillApi.create(data)
    return response.data
  }

  async function updateSkill(id: string, data: UpdateSkillRequest) {
    const response = await skillApi.update(id, data)
    return response.data
  }

  async function deleteSkill(id: string, permanent = false) {
    await skillApi.delete(id, permanent)
    // 从列表中移除
    const index = skills.value.findIndex(s => s.id === id)
    if (index > -1) {
      skills.value.splice(index, 1)
    }
  }

  return {
    skills,
    currentSkill,
    loading,
    total,
    fetchSkills,
    fetchSkillDetail,
    createSkill,
    updateSkill,
    deleteSkill
  }
})
```

---

## 路由配置

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/auth/login',
    name: 'login',
    component: () => import('@/views/Auth/Login.vue'),
    meta: { title: '登录', guest: true }
  },
  {
    path: '/auth/register',
    name: 'register',
    component: () => import('@/views/Auth/Register.vue'),
    meta: { title: '注册', guest: true }
  },
  {
    path: '/skills',
    name: 'skill-list',
    component: () => import('@/views/Skills/SkillList.vue'),
    meta: { title: 'Skills 列表' }
  },
  {
    path: '/skills/create',
    name: 'skill-create',
    component: () => import('@/views/Skills/SkillCreate.vue'),
    meta: { title: '创建 Skill', requiresAuth: true }
  },
  {
    path: '/skills/:id',
    name: 'skill-detail',
    component: () => import('@/views/Skills/SkillDetail.vue'),
    meta: { title: 'Skill 详情' }
  },
  {
    path: '/skills/:id/edit',
    name: 'skill-edit',
    component: () => import('@/views/Skills/SkillEdit.vue'),
    meta: { title: '编辑 Skill', requiresAuth: true }
  },
  {
    path: '/market',
    name: 'skill-market',
    component: () => import('@/views/Skills/SkillMarket.vue'),
    meta: { title: 'Skill 市场' }
  },
  {
    path: '/agents',
    name: 'agent-list',
    component: () => import('@/views/Agents/AgentList.vue'),
    meta: { title: 'Agents 列表', requiresAuth: true }
  },
  {
    path: '/agents/create',
    name: 'agent-create',
    component: () => import('@/views/Agents/AgentBuilder.vue'),
    meta: { title: '创建 Agent', requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/Dashboard/Overview.vue'),
    meta: { title: '仪表盘', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 需要认证的页面
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  }
  // 已登录用户访问登录/注册页，跳转到首页
  else if (to.meta.guest && authStore.isLoggedIn) {
    next({ name: 'home' })
  }
  else {
    next()
  }
})

export default router
```

---

## API 客户端封装

```typescript
import axios, { AxiosError } from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore()
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // 响应拦截器
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response.data,
      (error: AxiosError) => {
        if (error.response) {
          const status = error.response.status
          const message = (error.response.data as any)?.message || '请求失败'

          switch (status) {
            case 401:
              ElMessage.error('未授权，请重新登录')
              const authStore = useAuthStore()
              authStore.logout()
              window.location.href = '/auth/login'
              break
            case 403:
              ElMessage.error('无权限访问')
              break
            case 404:
              ElMessage.error('资源不存在')
              break
            case 500:
              ElMessage.error('服务器错误')
              break
            default:
              ElMessage.error(message)
          }
        } else {
          ElMessage.error('网络错误，请检查网络连接')
        }

        return Promise.reject(error)
      }
    )
  }

  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.client.get(url, config)
  }

  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.client.post(url, data, config)
  }

  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.client.put(url, data, config)
  }

  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.client.delete(url, config)
  }
}

export const apiClient = new ApiClient()
```

---

## 下一步

查看部署指南：`04-deployment-guide.md`
