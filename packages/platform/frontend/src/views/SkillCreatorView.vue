<template>
  <div class="skill-creator">
    <!-- 顶部导航栏 -->
    <div class="top-bar">
      <div class="top-bar-left">
        <el-button :icon="ArrowLeft" text @click="$router.back()">返回</el-button>
        <span class="skill-name">技能创建器 · 渐进式构建</span>
      </div>
      <div class="top-bar-right">
        <el-tag v-if="currentPhase" type="info">
          {{ currentPhase }}
        </el-tag>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：对话 + Log 进度区 (50%) -->
      <div class="left-panel">
        <!-- Log 风格进度显示 -->
        <div class="log-panel">
          <div class="log-header">
            <el-icon><Document /></el-icon>
            <span>构建日志</span>
            <el-button v-if="logs.length > 0" text size="small" @click="clearLogs">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <div class="log-content" ref="logRef">
            <div
              v-for="(log, idx) in logs"
              :key="idx"
              class="log-entry"
              :class="log.type"
            >
              <span class="log-time">{{ log.time }}</span>
              <span class="log-icon">{{ getLogIcon(log.type) }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
            <!-- 加载动画 -->
            <div v-if="isLoading" class="log-entry loading">
              <span class="log-time">{{ getCurrentTime() }}</span>
              <span class="log-icon">⏳</span>
              <span class="log-message">
                <span class="loading-dots"></span>
              </span>
            </div>
          </div>
        </div>

        <!-- 4阶段进度条 -->
        <div v-if="currentQuestion > 0 || isSummary" class="progress-panel">
          <div class="progress-header">
            <el-icon><TrendCharts /></el-icon>
            <span>创建进度</span>
            <span class="progress-text">{{ currentQuestion }}/4 阶段</span>
          </div>
          <div class="progress-steps">
            <div
              v-for="step in 4"
              :key="step"
              class="progress-step"
              :class="{
                'completed': step < currentQuestion,
                'active': step === currentQuestion && !isSummary,
                'pending': step > currentQuestion
              }"
            >
              <div class="step-circle">
                <el-icon v-if="step < currentQuestion"><CircleCheck /></el-icon>
                <span v-else>{{ step }}</span>
              </div>
              <div class="step-label">
                <span class="step-name">{{ getStepName(step) }}</span>
                <span v-if="step < currentQuestion" class="step-score">{{ getStepScore(step) }}</span>
              </div>
            </div>
          </div>
          <div class="progress-bar-container">
            <div class="progress-bar-track">
              <div class="progress-bar-fill" :style="{ width: `${progressPercentage}%` }"></div>
            </div>
          </div>
        </div>

        <!-- AI 对话区 -->
        <div class="chat-panel">
          <div class="chat-messages" ref="messagesRef">
            <!-- 欢迎/开始消息 -->
            <div v-if="messages.length === 0" class="message ai">
              <div class="message-content">
                <div class="ai-avatar">
                  <el-icon><ChatDotRound /></el-icon>
                </div>
                <div class="text-content">
                  <p>你好！我是技能创建助手。</p>
                  <p>我会通过渐进式对话，帮助你构建完整的 AgentScope 技能。</p>
                  <p>每一步都会实时更新右侧的文件结构。</p>
                  <el-button type="primary" @click="startSession" :loading="isLoading">
                    开始创建
                  </el-button>
                </div>
              </div>
            </div>

            <!-- 问题消息 -->
            <div v-for="msg in messages" :key="msg.id" class="message" :class="msg.role">
              <div class="message-content">
                <!-- AI 消息 -->
                <template v-if="msg.role === 'ai'">
                  <div v-if="msg.type === 'question'" class="question-content">
                    <div class="ai-avatar">
                      <el-icon><ChatDotRound /></el-icon>
                    </div>
                    <div class="question-body">
                      <!-- 维度标签 -->
                      <div class="dimension-badge" :class="msg.responseType">
                        <el-icon><Sunny /></el-icon>
                        <span>{{ msg.dimensionName }}</span>
                        <span v-if="msg.score !== undefined" class="score-badge" :class="getScoreClass(msg.score)">
                          {{ msg.score }}分
                        </span>
                      </div>

                      <!-- 上一阶段完成提示（用于 next_dimension） -->
                      <div v-if="msg.previousScore !== undefined" class="previous-stage-completion">
                        <el-icon><CircleCheck /></el-icon>
                        <span>
                          阶段 {{ msg.previousDimension }} 完成！评分
                          <strong :class="getScoreClass(msg.previousScore)">{{ msg.previousScore }}/100</strong>
                          {{ msg.previousScore >= 91 ? '✅ 优秀' : '⚠️ 需改进' }}
                        </span>
                      </div>

                      <h3>{{ msg.questionText }}</h3>

                      <!-- 评分详情（仅用于 follow_up） -->
                      <div v-if="msg.score !== undefined && msg.responseType === 'follow_up'" class="score-detail">
                        <div class="score-bar-container">
                          <div class="score-bar-track">
                            <div class="score-bar-fill" :style="{ width: `${msg.score}%` }" :class="getScoreClass(msg.score)"></div>
                          </div>
                          <span class="score-text">{{ msg.score }}/100</span>
                        </div>
                        <p v-if="msg.reasoning" class="reasoning">{{ msg.reasoning }}</p>
                      </div>

                      <!-- 推荐选项 -->
                      <div v-if="msg.recommendedOptions && msg.recommendedOptions.length > 0" class="recommended-options">
                        <div class="options-header">
                          <el-icon><MagicStick /></el-icon>
                          <span>推荐选项（点击选择）</span>
                        </div>
                        <div class="options-grid">
                          <div
                            v-for="opt in msg.recommendedOptions"
                            :key="opt.id"
                            class="option-card"
                            @click="selectRecommendedOption(opt)"
                          >
                            <el-icon><Plus /></el-icon>
                            <span>{{ opt.text }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- 总结消息 -->
                  <div v-else-if="msg.type === 'summary'" class="summary-content">
                    <div class="ai-avatar">
                      <el-icon><CircleCheck /></el-icon>
                    </div>
                    <div class="summary-body">
                      <h3>技能创建完成</h3>
                      <p>{{ msg.message }}</p>
                      <div class="summary-actions">
                        <el-button type="primary" @click="confirmMetadata">保存技能</el-button>
                        <el-button @click="restartSession">重新创建</el-button>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- 用户消息 -->
                <template v-else>
                  <div class="user-bubble">{{ msg.content }}</div>
                </template>
              </div>
            </div>
          </div>

          <!-- 输入区 -->
          <div v-if="currentQuestion && !isSummary" class="chat-input">
            <el-input
              v-model="userInput"
              type="textarea"
              :rows="2"
              :placeholder="currentPlaceholder"
              @keydown.ctrl.enter="sendAnswer"
            />
            <div class="input-actions">
              <span class="input-hint">Ctrl + Enter 发送</span>
              <div class="input-buttons">
                <el-button text :loading="isLoading" @click="skipQuestion">
                  跳过
                </el-button>
                <el-button type="primary" :loading="isLoading" :disabled="!userInput.trim()" @click="sendAnswer">
                  发送
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：资源管理器 (50%) - 实时同步 -->
      <div class="right-panel">
        <div class="file-explorer">
          <!-- Explorer Header -->
          <div class="explorer-header">
            <div class="explorer-title">
              <el-icon><Folder /></el-icon>
              <span>{{ skillName || 'untitled-skill' }}</span>
            </div>
            <div class="explorer-status">
              <el-tag v-if="buildStatus" :type="buildStatus.type" size="small">
                {{ buildStatus.text }}
              </el-tag>
            </div>
          </div>

          <!-- Progressive Disclosure 层级指示 -->
          <div class="disclosure-levels">
            <div class="level-item" :class="{ active: disclosureLevel >= 1 }">
              <div class="level-dot"></div>
              <div class="level-info">
                <span class="level-name">Level 1: Metadata</span>
                <span class="level-tokens">~100 tokens</span>
              </div>
            </div>
            <div class="level-item" :class="{ active: disclosureLevel >= 2 }">
              <div class="level-dot"></div>
              <div class="level-info">
                <span class="level-name">Level 2: Instructions</span>
                <span class="level-tokens">~5k tokens</span>
              </div>
            </div>
            <div class="level-item" :class="{ active: disclosureLevel >= 3 }">
              <div class="level-dot"></div>
              <div class="level-info">
                <span class="level-name">Level 3: Resources</span>
                <span class="level-tokens">按需加载</span>
              </div>
            </div>
          </div>

          <!-- File Tree -->
          <div class="file-tree">
            <!-- SKILL.md -->
            <div class="tree-item" :class="{ active: selectedFile === 'SKILL.md' }" @click="selectedFile = 'SKILL.md'">
              <div class="item-icon file-icon-md">M</div>
              <span class="item-name">SKILL.md</span>
              <span v-if="skillFiles.skillMd" class="item-status status-generated">已生成</span>
              <span v-else class="item-status status-pending">待生成</span>
            </div>

            <!-- scripts/ -->
            <div class="tree-item folder" @click="toggleFolder('scripts')">
              <div class="item-icon folder-icon">
                <el-icon><component :is="folders.scripts ? 'FolderOpened' : 'Folder'" /></el-icon>
              </div>
              <span class="item-name">scripts/</span>
            </div>
            <div v-show="folders.scripts" class="tree-children">
              <div class="tree-item" :class="{ active: selectedFile === 'scripts/tools.py' }">
                <div class="item-icon file-icon-py">P</div>
                <span class="item-name">tools.py</span>
                <span v-if="skillFiles.toolsPy" class="item-status status-generated">已生成</span>
                <span v-else class="item-status status-pending">待生成</span>
              </div>
            </div>

            <!-- references/ -->
            <div class="tree-item folder" @click="toggleFolder('references')">
              <div class="item-icon folder-icon">
                <el-icon><component :is="folders.references ? 'FolderOpened' : 'Folder'" /></el-icon>
              </div>
              <span class="item-name">references/</span>
            </div>
            <div v-show="folders.references" class="tree-children">
              <div class="tree-item">
                <div class="item-icon file-icon-txt">R</div>
                <span class="item-name">README.md</span>
                <span class="item-status status-dimmed">可选</span>
              </div>
            </div>

            <!-- assets/ -->
            <div class="tree-item folder" @click="toggleFolder('assets')">
              <div class="item-icon folder-icon">
                <el-icon><component :is="folders.assets ? 'FolderOpened' : 'Folder'" /></el-icon>
              </div>
              <span class="item-name">assets/</span>
            </div>
            <div v-show="folders.assets" class="tree-children">
              <div class="tree-item">
                <div class="item-icon file-icon-img">I</div>
                <span class="item-name">icon.png</span>
                <span class="item-status status-dimmed">可选</span>
              </div>
            </div>
          </div>

          <!-- File Preview -->
          <div class="file-preview">
            <div class="preview-header">
              <span>{{ selectedFile || '选择文件查看预览' }}</span>
              <el-button v-if="selectedFile && selectedFile !== 'preview'" text size="small" @click="selectedFile = 'preview'">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
            <div class="preview-content">
              <!-- SKILL.md 预览 -->
              <div v-if="selectedFile === 'SKILL.md'" class="code-preview">
                <pre v-if="skillFiles.skillMd"><code>{{ skillFiles.skillMd }}</code></pre>
                <div v-else class="empty-state">
                  <el-icon><Document /></el-icon>
                  <p>SKILL.md 将在对话过程中逐步生成...</p>
                </div>
              </div>

              <!-- tools.py 预览 -->
              <div v-else-if="selectedFile === 'scripts/tools.py'" class="code-preview">
                <pre v-if="skillFiles.toolsPy"><code class="language-python">{{ skillFiles.toolsPy }}</code></pre>
                <div v-else class="empty-state">
                  <el-icon><Document /></el-icon>
                  <p>tools.py 将根据技能需求生成...</p>
                </div>
              </div>

              <!-- 默认空状态 -->
              <div v-else class="empty-state">
                <el-icon><FolderOpened /></el-icon>
                <p>点击文件名查看内容</p>
                <p class="empty-hint">文件会随着对话进度实时更新</p>
              </div>
            </div>
          </div>

          <!-- Token 统计 -->
          <div class="token-stats">
            <div class="stats-row">
              <span class="stats-label">Token 估算</span>
              <span class="stats-value">{{ totalTokens }} tokens</span>
            </div>
            <div class="stats-breakdown">
              <div class="stat-item">
                <span class="stat-dot metadata"></span>
                <span class="stat-label">Metadata: {{ metadataTokens }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-dot instructions"></span>
                <span class="stat-label">Instructions: {{ instructionsTokens }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  ChatDotRound,
  Sunny,
  CircleCheck,
  Folder,
  FolderOpened,
  Document,
  Delete,
  Plus,
  Close,
  MagicStick,
} from '@element-plus/icons-vue'
import { skillCreatorApi } from '@/api/skillCreator'

const router = useRouter()

// === 状态管理 ===
const sessionId = ref<string | null>(null)
const isLoading = ref(false)
const isSummary = ref(false)
const userInput = ref('')
const currentPlaceholder = ref('')
const currentQuestion = ref(0)
const currentDimension = ref('')
const currentPhase = ref('')

// Log 相关
interface LogEntry {
  time: string
  type: 'info' | 'success' | 'warning' | 'error' | 'system'
  message: string
}
const logs = ref<LogEntry[]>([])

// 消息历史
interface Message {
  id: string
  role: 'user' | 'ai'
  type: 'text' | 'question' | 'summary'
  content?: string
  questionText?: string
  guidance?: string
  placeholder?: string
  examples?: string[]
  suggestions?: string[]
  previousAnswer?: string
  skillMetadata?: any
  progress?: { current: number; total: number; percentage: number }
  message?: string
  nextStep?: string
  responseType?: 'follow_up' | 'next_dimension'
  dimensionName?: string
  score?: number
  reasoning?: string
  recommendedOptions?: Array<{ id: string; text: string }>
  previousScore?: number  // 上一阶段的评分（用于 next_dimension）
  previousDimension?: number  // 上一阶段编号（用于 next_dimension）
}
const messages = ref<Message[]>([])

// 技能文件内容
const skillFiles = ref({
  skillMd: '',
  toolsPy: '',
})

// 资源管理器状态
const selectedFile = ref<string>('preview')
const skillName = ref('untitled-skill')
const folders = ref({
  scripts: true,
  references: false,
  assets: false,
})

// Progressive Disclosure 状态
const disclosureLevel = ref(0) // 0-2
const buildStatus = ref<{ type: '' | 'success' | 'warning'; text: string } | null>(null)

// Token 统计
const metadataTokens = ref(0)
const instructionsTokens = ref(0)
const totalTokens = computed(() => metadataTokens.value + instructionsTokens.value)

// 4阶段进度追踪
const stageProgress = ref([
  { name: '核心价值', score: null as number | null, completed: false },
  { name: '使用场景', score: null as number | null, completed: false },
  { name: '别名偏好', score: null as number | null, completed: false },
  { name: '边界资源', score: null as number | null, completed: false },
])

// Refs
const messagesRef = ref<HTMLElement>()
const logRef = ref<HTMLElement>()

// === 计算属性 ===
const progressPercentage = computed(() => {
  if (isSummary.value) return 100
  return currentQuestion.value ? currentQuestion.value * 25 : 0
})

// === 阶段进度函数 ===
const getStepName = (step: number) => {
  return stageProgress.value[step - 1]?.name || `阶段${step}`
}

const getStepScore = (step: number) => {
  const score = stageProgress.value[step - 1]?.score
  return score !== null ? `${score}分` : ''
}

const updateStageProgress = (stage: number, score: number, name?: string) => {
  if (stage >= 1 && stage <= 4) {
    stageProgress.value[stage - 1].score = score
    stageProgress.value[stage - 1].completed = score >= 91
    if (name) {
      stageProgress.value[stage - 1].name = name
    }
  }
}

// === Log 功能 ===
const addLog = (message: string, type: LogEntry['type'] = 'info') => {
  logs.value.push({
    time: getCurrentTime(),
    type,
    message,
  })
  nextTick(() => {
    if (logRef.value) {
      logRef.value.scrollTop = logRef.value.scrollHeight
    }
  })
}

const getCurrentTime = () => {
  const now = new Date()
  return now.toTimeString().slice(0, 8)
}

const getLogIcon = (type: LogEntry['type']) => {
  const icons = {
    info: 'ℹ️',
    success: '✅',
    warning: '⚠️',
    error: '❌',
    system: '⚙️',
  }
  return icons[type] || icons.info
}

const clearLogs = () => {
  logs.value = []
}

// === 技能文件同步更新 ===
const updateSkillFile = (file: 'SKILL.md' | 'tools.py', content: string) => {
  if (file === 'SKILL.md') {
    skillFiles.value.skillMd = content
    metadataTokens.value = content.length / 4 // 粗略估算
  } else {
    skillFiles.value.toolsPy = content
  }
  addLog(`文件更新: ${file}`, 'system')
}

// === 对话功能 ===
const startSession = async () => {
  isLoading.value = true
  addLog('初始化 Agent...', 'system')

  try {
    const response = await skillCreatorApi.createAgentSession(true)
    sessionId.value = response.session_id

    addLog('会话已创建', 'success')
    addLog(`进入阶段 1/4: ${response.dimension_name}`, 'info')

    // 初始化 SKILL.md 基础结构
    initSkillMd(response.dimension_name)

    addQuestionMessage(response)
    currentQuestion.value = response.progress?.current || 1
    currentPlaceholder.value = response.placeholder || ''

    messages.value.push({
      id: Date.now().toString(),
      role: 'ai',
      type: 'text',
      content: '让我们开始创建你的技能。请描述你想解决的问题。',
    })

    disclosureLevel.value = 1 // Level 1: Metadata
    buildStatus.value = { type: 'success', text: '构建中' }
  } catch (error) {
    console.error('Failed to create session:', error)
    addLog('创建会话失败', 'error')
    ElMessage.error('创建会话失败，请重试')
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const sendAnswer = async () => {
  if (!userInput.value.trim() || isLoading.value || !sessionId.value) return

  const answer = userInput.value
  const previousDimension = currentDimension.value
  userInput.value = ''

  // 添加用户消息
  messages.value.push({
    id: Date.now().toString(),
    role: 'user',
    type: 'text',
    content: answer,
  })

  addLog(`用户回答: ${answer.slice(0, 50)}${answer.length > 50 ? '...' : ''}`, 'info')

  await nextTick()
  scrollToBottom()

  isLoading.value = true

  try {
    const response = await skillCreatorApi.agentChat(sessionId.value, answer)

    // 处理错误响应
    if (response.type === 'error' || response.type === 'parse_error') {
      addLog(`Agent 调用失败: ${response.error || response.reasoning || '未知错误'}`, 'error')
      addLog(`评分: ${response.score}/100 (表示错误)`, 'error')

      // 显示错误消息
      messages.value.push({
        id: Date.now().toString(),
        role: 'ai',
        type: 'question',
        questionText: response.follow_up_question || '发生错误，请重试',
        responseType: 'error',
        dimensionName: response.dimension_name || '错误',
        score: response.score,
        reasoning: response.reasoning,
        recommendedOptions: response.recommended_options || [],
      })
      return
    }

    // 更新状态
    if (response.type === 'next_dimension' || response.type === 'follow_up') {
      currentQuestion.value = response.progress?.current || 0
      currentPlaceholder.value = response.placeholder || ''

      // 记录评分
      if (response.score !== undefined) {
        const scoreNum = response.score
        let logType: 'success' | 'warning' | 'error' = 'warning'
        if (scoreNum >= 91) logType = 'success'
        else if (scoreNum < 0) logType = 'error'

        addLog(`LLM 评分: ${response.score}/100`, logType)
        if (response.reasoning) {
          addLog(`评分理由: ${response.reasoning}`, 'system')
        }
      }

      // 记录阶段变更并更新 SKILL.md
      if (response.type === 'next_dimension') {
        // 更新上一阶段的评分
        if (response.score !== undefined && response.progress?.current) {
          const previousStage = response.progress.current - 1
          updateStageProgress(previousStage, response.score)
        }

        addLog(`进入阶段 ${response.progress?.current}/4: ${response.dimension_name}`, 'success')
        // 进入新维度时，更新上一维度的内容到 SKILL.md
        if (previousDimension && answer) {
          updateSkillMdProgress(previousDimension, answer)
        }
        disclosureLevel.value = Math.min(disclosureLevel.value + 1, 2) // Level 2: Instructions
        // 激活 Level 3 当完成所有维度
        if (response.progress?.current >= 4) {
          disclosureLevel.value = 3
        }
      } else {
        addLog(`需要补充信息 (${response.dimension_name})`, 'warning')
        // 追问时也更新当前维度的内容
        if (previousDimension) {
          updateSkillMdProgress(previousDimension, answer)
        }
      }

      addQuestionMessage(response)
    } else if (response.type === 'summary') {
      isSummary.value = true
      currentQuestion.value = 4
      disclosureLevel.value = 3 // Level 3: Resources (完成时激活)

      addLog('所有维度收集完成', 'success')
      addLog('生成最终技能配置...', 'system')

      // 更新最后一个维度的内容
      if (previousDimension && answer) {
        updateSkillMdProgress(previousDimension, answer)
      }

      // 生成完整的 SKILL.md
      generateFinalSkillMd(response.skill_metadata)

      messages.value.push({
        id: Date.now().toString(),
        role: 'ai',
        type: 'summary',
        message: response.message,
        skillMetadata: response.skill_metadata,
        progress: response.progress,
      })

      buildStatus.value = { type: 'success', text: '构建完成' }
    }

  } catch (error) {
    console.error('Chat failed:', error)
    addLog('发送失败', 'error')
    ElMessage.error('发送失败，请重试')
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const addQuestionMessage = (response: any) => {
  const questionText = response.follow_up_question || response.question || response.question_text || ''

  messages.value.push({
    id: Date.now().toString(),
    role: 'ai',
    type: 'question',
    questionText: questionText,
    guidance: response.guidance,
    placeholder: response.placeholder,
    examples: response.examples || [],
    suggestions: response.suggestions || [],
    progress: response.progress,
    responseType: response.type,
    dimensionName: response.dimension_name,
    score: response.type === 'next_dimension' ? undefined : response.score, // next_dimension 不显示 score（那是上一阶段的）
    reasoning: response.reasoning,
    recommendedOptions: response.recommended_options || [],
    previousScore: response.type === 'next_dimension' ? response.score : undefined, // 上一阶段的评分
    previousDimension: response.type === 'next_dimension' ? (response.progress?.current - 1) : undefined, // 上一阶段编号
  })

  currentDimension.value = response.current_dimension
}

// 选择推荐选项
const selectRecommendedOption = async (option: { id: string; text: string }) => {
  userInput.value = option.text
  await sendAnswer()
}

// 跳过问题
const skipQuestion = async () => {
  if (!sessionId.value || isLoading.value) return

  addLog('用户选择跳过当前问题', 'warning')

  isLoading.value = true
  try {
    const response = await skillCreatorApi.agentChat(sessionId.value, '[用户选择跳过]')

    if (response.type === 'next_dimension' || response.type === 'follow_up') {
      currentQuestion.value = response.progress?.current || 0
      currentPlaceholder.value = response.placeholder || ''
      addQuestionMessage(response)

      if (response.type === 'next_dimension') {
        addLog(`进入阶段 ${response.progress?.current}/4: ${response.dimension_name}`, 'info')
      }
    } else if (response.type === 'summary') {
      isSummary.value = true
      currentQuestion.value = 4
      addLog('完成创建（用户跳过部分问题）', 'success')
      buildStatus.value = { type: 'warning', text: '部分完成' }
    }
  } catch (error) {
    console.error('Skip failed:', error)
    addLog('跳过失败', 'error')
    ElMessage.error('操作失败，请重试')
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

// === 技能文件生成 ===
const initSkillMd = (dimensionName: string) => {
  const timestamp = new Date().toISOString()
  skillFiles.value.skillMd = `---
name: untitled-skill
description: 技能描述
main_alias: 执行技能
category: general
created_at: ${timestamp}
---

# Untitled Skill

> 创建于 ${new Date().toLocaleString('zh-CN')}

## 💡 快速开始

\`\`\`
执行技能 [参数]
\`\`\`

## 📋 当前进度

- ✅ ${dimensionName}: 收集中...

## 🎯 核心价值

待填写...

## 📋 使用场景

待填写...

## ⚠️ 边界限制

待填写...
`
  metadataTokens.value = 200
}

const updateSkillMdProgress = (dimension: string, answer: string) => {
  // 根据维度更新 SKILL.md 的对应部分
  const sectionNames: Record<string, string> = {
    core_value: '核心价值',
    usage_scenario: '使用场景',
    alias_preference: '别名系统',
    boundaries: '边界限制',
  }

  const sectionName = sectionNames[dimension] || dimension
  const sectionHeader = `## 🎯 ${sectionName}`

  // 查找并替换对应部分
  const lines = skillFiles.value.skillMd.split('\n')
  let startIndex = -1
  let endIndex = lines.length

  // 找到对应section的开始位置
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes(sectionHeader)) {
      startIndex = i
      break
    }
  }

  // 找到下一个section的位置（作为结束位置）
  if (startIndex >= 0) {
    for (let i = startIndex + 1; i < lines.length; i++) {
      if (lines[i].startsWith('## ') && i > startIndex + 1) {
        endIndex = i
        break
      }
    }

    // 构建新的内容
    const beforeSection = lines.slice(0, startIndex + 1).join('\n')
    const afterSection = lines.slice(endIndex).join('\n')

    // 更新该部分的内容（追加新回答）
    const currentSectionContent = lines.slice(startIndex + 1, endIndex).join('\n')
    const updatedSectionContent = currentSectionContent.includes('待填写')
      ? answer
      : `${currentSectionContent}\n\n${answer}`

    skillFiles.value.skillMd = `${beforeSection}\n\n${updatedSectionContent}\n${afterSection}`

    // 更新 token 估算
    instructionsTokens.value = skillFiles.value.skillMd.length / 4

    addLog(`SKILL.md 实时更新: ${sectionName}`, 'system')
  }
}

const generateFinalSkillMd = (metadata: any) => {
  const { skill_name, core_value, usage_scenario, main_alias, context_aliases, command_alias, api_alias, boundaries, category } = metadata

  skillFiles.value.skillMd = `---
name: ${skill_name}
description: ${core_value?.slice(0, 100) || '技能描述'}
main_alias: ${main_alias || '执行技能'}
category: ${category || 'general'}
---

# ${skill_name.replace(/-/g, ' ').replace(/\b\w/g, (w: string) => w.charAt(0).toUpperCase() + w.slice(1))}

## 🎯 核心价值

${core_value || '待填写'}

## 📋 使用场景

${usage_scenario || '待填写'}

## 📱 所有可用别名

| 类型 | 调用方式 | 示例 | 说明 |
|------|----------|------|------|
| **主别名** | 自然语言 | \`${main_alias || '执行技能'} ...\` | 最常用 |
${context_aliases?.map((alias: string) => `| 上下文别名 | 自然语言 | \`${alias}\` | 专用场景 |`).join('') || ''}
| **命令别名** | 快捷命令 | \`/${command_alias || 'skill'} ...\` | 高级用法 |
| **API别名** | 程序调用 | \`${api_alias || 'skill_name'}\` | 系统集成 |

## ⚠️ 边界限制

${boundaries || '待填写'}

## 🔧 技能能力

待实现...

---

*由 LingNexus Skill Creator 自动生成*
`

  instructionsTokens.value = skillFiles.value.skillMd.length / 4
  addLog('SKILL.md 生成完成', 'success')
}

// === 工具函数 ===
const getScoreClass = (score: number) => {
  if (score < 0) return 'score-error'  // 负数表示错误
  if (score >= 91) return 'score-excellent'
  if (score >= 81) return 'score-good'
  if (score >= 61) return 'score-medium'
  if (score >= 41) return 'score-low'
  return 'score-poor'
}

const toggleFolder = (folder: string) => {
  folders.value[folder as keyof typeof folders.value] = !folders.value[folder as keyof typeof folders.value]
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const confirmMetadata = async () => {
  if (!sessionId.value) return

  isLoading.value = true
  try {
    const response = await skillCreatorApi.saveSkillFromSession(sessionId.value)
    addLog(`技能保存成功: ${response.skill_name}`, 'success')
    ElMessage.success({
      message: `技能 "${response.skill_name}" 保存成功！`,
      duration: 3000,
      onClose: () => {
        // 跳转到 Marketplace（无需登录）
        router.push('/marketplace')
      }
    })
  } catch (error) {
    console.error('Failed to save skill:', error)
    addLog('保存失败', 'error')
    ElMessage.error('保存失败，请重试')
  } finally {
    isLoading.value = false
  }
}

const restartSession = () => {
  sessionId.value = null
  currentQuestion.value = 0
  currentPlaceholder.value = ''
  isSummary.value = false
  messages.value = []
  logs.value = []
  skillFiles.value = { skillMd: '', toolsPy: '' }
  skillName.value = 'untitled-skill'
  disclosureLevel.value = 0
  buildStatus.value = null
  metadataTokens.value = 0
  instructionsTokens.value = 0
}
</script>

<style scoped>
/* ===== 整体布局 ===== */
.skill-creator {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #f5f5f7 0%, #e8e8ed 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
}

/* ===== 顶部栏 ===== */
.top-bar {
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.skill-name {
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
}

/* ===== 主内容区 ===== */
.main-content {
  flex: 1;
  display: flex;
  gap: 1px;
  background: rgba(0, 0, 0, 0.08);
}

.left-panel,
.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f5f5f7;
  overflow: hidden;
}

/* ===== Log 面板 ===== */
.log-panel {
  height: 200px;
  display: flex;
  flex-direction: column;
  background: #1d1d1f;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.log-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: #f5f5f7;
  font-size: 13px;
  font-weight: 500;
}

.log-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 16px;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace;
  font-size: 12px;
  line-height: 1.6;
}

.log-entry {
  display: flex;
  gap: 12px;
  margin-bottom: 4px;
  color: #a1a1aa;
}

.log-entry.info { color: #60a5fa; }
.log-entry.success { color: #34d399; }
.log-entry.warning { color: #fbbf24; }
.log-entry.error { color: #f87171; }
.log-entry.system { color: #8b5cf6; }

.log-time {
  color: #52525b;
  min-width: 70px;
}

.log-icon {
  min-width: 20px;
}

.log-message {
  flex: 1;
  word-break: break-all;
}

.loading-dots::after {
  content: '';
  animation: dots 1.5s infinite;
}

@keyframes dots {
  0%, 20% { content: '.'; }
  40% { content: '..'; }
  60%, 100% { content: '...'; }
}

/* ===== 4阶段进度条 ===== */
.progress-panel {
  background: white;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  padding: 12px 16px;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.progress-text {
  margin-left: auto;
  color: #86868b;
  font-size: 12px;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 8px;
}

.progress-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.step-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  background: #f5f5f7;
  color: #86868b;
  transition: all 0.3s ease;
}

.progress-step.completed .step-circle {
  background: #34c759;
  color: white;
}

.progress-step.active .step-circle {
  background: #007aff;
  color: white;
  box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2);
}

.step-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  text-align: center;
}

.step-name {
  font-size: 11px;
  font-weight: 500;
  color: #1d1d1f;
}

.progress-step.completed .step-name {
  color: #34c759;
}

.progress-step.active .step-name {
  color: #007aff;
}

.progress-step.pending .step-name {
  color: #86868b;
}

.step-score {
  font-size: 10px;
  font-weight: 600;
  color: #34c759;
}

.progress-bar-container {
  height: 4px;
  background: #f5f5f7;
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar-track {
  height: 100%;
  background: #e5e5ea;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #007aff, #34c759);
  transition: width 0.5s ease;
  border-radius: 2px;
}

/* ===== 上一阶段完成提示 ===== */
.previous-stage-completion {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  margin-bottom: 12px;
  background: linear-gradient(135deg, rgba(52, 199, 89, 0.1), rgba(52, 199, 89, 0.05));
  border: 1px solid rgba(52, 199, 89, 0.2);
  border-radius: 8px;
  font-size: 13px;
  color: #1d1d1f;
}

.previous-stage-completion .el-icon {
  color: #34c759;
  font-size: 16px;
}

.previous-stage-completion strong {
  margin: 0 4px;
}

/* ===== 对话面板 ===== */
.chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message {
  margin-bottom: 20px;
}

.message.user .message-content {
  display: flex;
  justify-content: flex-end;
}

.user-bubble {
  background: #007aff;
  color: white;
  padding: 12px 18px;
  border-radius: 18px;
  max-width: 70%;
}

.question-content {
  display: flex;
  gap: 12px;
}

.ai-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #007aff 0%, #5ac8fa 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.question-body {
  flex: 1;
  max-width: 90%;
}

.dimension-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: linear-gradient(135deg, rgba(0, 122, 255, 0.1) 0%, rgba(88, 200, 250, 0.1) 100%);
  border-radius: 20px;
  font-size: 14px;
  color: #007aff;
  margin-bottom: 14px;
}

.dimension-badge.follow_up {
  background: linear-gradient(135deg, rgba(255, 149, 0, 0.1) 0%, rgba(255, 159, 64, 0.1) 100%);
  color: #ff9500;
}

.score-badge {
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.question-body h3 {
  font-size: 18px;
  margin: 0 0 14px 0;
  color: #1d1d1f;
  font-weight: 600;
}

.score-detail {
  margin: 16px 0;
}

.score-bar-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-bar-track {
  flex: 1;
  height: 8px;
  background: rgba(0, 0, 0, 0.08);
  border-radius: 4px;
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.score-bar-fill.score-excellent { background: linear-gradient(90deg, #34c759, #30d158); }
.score-bar-fill.score-good { background: linear-gradient(90deg, #30d158, #34c759); }
.score-bar-fill.score-medium { background: linear-gradient(90deg, #ff9500, #ff6b00); }
.score-bar-fill.score-low { background: linear-gradient(90deg, #ff6b00, #ff3b30); }
.score-bar-fill.score-poor { background: linear-gradient(90deg, #ff3b30, #ff453a); }
.score-bar-fill.score-error { background: linear-gradient(90deg, #8e8e93, #636366); }

.score-text {
  font-weight: 600;
  font-size: 14px;
  min-width: 50px;
  text-align: right;
}

.reasoning {
  margin: 8px 0 0 0;
  font-size: 13px;
  color: #86868b;
  font-style: italic;
}

/* 推荐选项 */
.recommended-options {
  margin: 16px 0;
}

.options-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #007aff;
  font-weight: 500;
  margin-bottom: 10px;
}

.options-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: white;
  border: 1px solid rgba(0, 122, 255, 0.2);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option-card:hover {
  background: rgba(0, 122, 255, 0.05);
  transform: translateX(4px);
}

.option-card .el-icon {
  color: #007aff;
  font-size: 16px;
}

.option-card span {
  font-size: 14px;
  color: #1d1d1f;
}

/* 总结内容 */
.summary-content {
  display: flex;
  gap: 12px;
}

.summary-body {
  flex: 1;
}

.summary-body h3 {
  font-size: 18px;
  color: #34c759;
  margin: 0 0 10px 0;
}

.summary-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}

/* ===== 输入区 ===== */
.chat-input {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.chat-input .el-textarea {
  font-size: 14px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.input-hint {
  font-size: 12px;
  color: #86868b;
}

.input-buttons {
  display: flex;
  gap: 8px;
}

/* ===== 右侧资源管理器 ===== */
.file-explorer {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-left: 1px solid rgba(0, 0, 0, 0.08);
}

.explorer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.explorer-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
}

/* Progressive Disclosure 层级 */
.disclosure-levels {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.level-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  opacity: 0.4;
  transition: opacity 0.3s ease;
}

.level-item.active {
  opacity: 1;
}

.level-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #d1d1d6;
}

.level-item.active .level-dot {
  background: #34c759;
}

.level-item.active:nth-child(1) .level-dot { background: #007aff; }
.level-item.active:nth-child(2) .level-dot { background: #30d158; }
.level-item.active:nth-child(3) .level-dot { background: #ff9500; }

.level-info {
  display: flex;
  flex-direction: column;
}

.level-name {
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.level-tokens {
  font-size: 11px;
  color: #86868b;
}

/* 文件树 */
.file-tree {
  padding: 8px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.tree-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.tree-item:hover {
  background: rgba(0, 0, 0, 0.04);
}

.tree-item.active {
  background: rgba(0, 122, 255, 0.1);
}

.item-icon {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 700;
  color: white;
}

.file-icon-md { background: linear-gradient(135deg, #9333ea, #7c3aed); }
.file-icon-py { background: linear-gradient(135deg, #ec4899, #db2777); }
.file-icon-txt { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.file-icon-img { background: linear-gradient(135deg, #10b981, #059669); }

.folder-icon {
  color: #007aff;
  font-size: 18px;
}

.item-name {
  flex: 1;
  font-size: 13px;
  color: #1d1d1f;
}

.item-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
}

.status-generated {
  background: rgba(52, 199, 89, 0.15);
  color: #34c759;
}

.status-pending {
  background: rgba(142, 142, 147, 0.15);
  color: #8e8e93;
}

.status-dimmed {
  background: rgba(142, 142, 147, 0.08);
  color: #a1a1aa;
}

.tree-children {
  padding-left: 24px;
}

/* 文件预览 */
.file-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: rgba(0, 0, 0, 0.02);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  font-size: 13px;
  font-weight: 500;
  color: #86868b;
}

.preview-content {
  flex: 1;
  overflow: auto;
  padding: 0;
}

.code-preview {
  height: 100%;
  background: #1d1d1f;
  margin: 0;
}

.code-preview pre {
  margin: 0;
  padding: 16px;
  font-size: 12px;
  line-height: 1.5;
  overflow: auto;
}

.code-preview code {
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  color: #a1a1aa;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #86868b;
}

.empty-state .el-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.empty-state p {
  margin: 4px 0;
}

.empty-hint {
  font-size: 12px;
}

/* Token 统计 */
.token-stats {
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.02);
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.stats-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.stats-label {
  font-size: 13px;
  color: #86868b;
}

.stats-value {
  font-size: 16px;
  font-weight: 600;
  color: #007aff;
}

.stats-breakdown {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.stat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.stat-dot.metadata { background: #007aff; }
.stat-dot.instructions { background: #34c759; }

.stat-label {
  color: #86868b;
}
</style>
