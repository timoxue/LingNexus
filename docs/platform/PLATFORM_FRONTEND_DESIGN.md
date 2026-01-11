# LingNexus Platform - 完整前端功能设计

## 🎯 产品愿景

**核心理念**："从 Skills 到能力的桥梁" - 让用户能够轻松发现、组合和使用 Skills，构建强大的 AI 能力。

---

## 📊 产品架构

```
┌─────────────────────────────────────────────────────────────┐
│                  LingNexus Platform                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Skills Market │  │Agent Builder │  │Workflow      │     │
│  │   Place      │  │   Studio     │  │   Studio     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│           ↓                  ↓                  ↓              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  My Skills   │  │  My Agents   │  │  My          │     │
│  │  (收藏)      │  │  (我的代理)  │  │  Workflows   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Execution Engine                        │  │
│  │  (执行引擎 - 协调 Skills, Agents, Workflows)       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Analytics & Community                   │  │
│  │  (使用统计、评分、推荐、团队协作)                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Skills Marketplace 2.0

### 1.1 首页设计

```vue
<template>
  <div class="skills-marketplace">
    <!-- 搜索栏 -->
    <div class="search-section">
      <el-input
        v-model="searchQuery"
        placeholder="搜索 Skills..."
        prefix-icon="Search"
        size="large"
        style="max-width: 500px"
      />
      <el-select v-model="selectedCategory" placeholder="全部分类" style="width: 150px">
        <el-option label="全部分类" value="" />
        <el-option label="医药" value="medical" />
        <el-option label="文档" value="document" />
        <el-option label="数据" value="data" />
        <el-option label="客服" value="service" />
      </el-select>
      <el-button type="primary" @click="$router.push('/skills/my')">⭐ 我的收藏</el-button>
    </div>

    <!-- 快速开始场景 -->
    <div class="quick-start">
      <h2>🎯 快速开始 - 选择场景，一键创建</h2>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="scenario-card" @click="filterByScenario('document')">
            <div class="scenario-icon">📄</div>
            <h3>文档处理</h3>
            <p>12 Skills</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="scenario-card" @click="filterByScenario('data')">
            <div class="scenario-icon">📊</div>
            <h3>数据分析</h3>
            <p>8 Skills</p>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="scenario-card" @click="filterByScenario('service')">
            <div class="scenario-icon">💬</div>
            <h3>客服助手</h3>
            <p>15 Skills</p>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 热门 Skills -->
    <div class="section">
      <h2>🔥 热门 Skills</h2>
      <el-row :gutter="20">
        <el-col :span="24" v-for="skill in hotSkills" :key="skill.id">
          <el-card class="skill-card">
            <div class="skill-header">
              <h3>{{ skill.name }}</h3>
              <el-tag :type="getCategoryTagType(skill.category)">
                {{ getCategoryLabel(skill.category) }}
              </el-tag>
            </div>
            <div class="skill-meta">
              <span>👤 {{ skill.creator_name }}</span>
              <span>⭐ {{ skill.rating }} ({{ skill.rating_count }})</span>
              <span>👁️ {{ skill.usage_count }}</span>
            </div>
            <p class="skill-description">{{ skill.description }}</p>
            <div class="skill-actions">
              <el-button type="primary" @click="trySkill(skill)">💬 立即试用</el-button>
              <el-button @click="createAgentFromSkill(skill)">🚀 创建 Agent</el-button>
              <el-button @click="viewSkillDetail(skill)">📖 查看详情</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 我的部门 Skills -->
    <div class="section" v-if="teamSkills.length > 0">
      <h2>📚 我的部门 ({{ userDepartment }})</h2>
      <!-- 类似上面的卡片列表 -->
    </div>

    <!-- 官方推荐 Skills -->
    <div class="section">
      <h2>✨ 官方推荐</h2>
      <!-- 官方认证的 Skills -->
    </div>
  </div>
</template>
```

### 1.2 Skill 详情页

```vue
<template>
  <div class="skill-detail">
    <!-- 基础信息 -->
    <div class="detail-header">
      <h1>{{ skill.name }}</h1>
      <div class="meta-info">
        <el-tag :type="getCategoryTagType(skill.category)">
          {{ getCategoryLabel(skill.category) }}
        </el-tag>
        <el-tag v-if="skill.is_official" type="success">✨ 官方认证</el-tag>
        <el-tag :type="skill.sharing_scope === 'public' ? 'success' : 'info'">
          {{ getScopeLabel(skill.sharing_scope) }}
        </el-tag>
      </div>
    </div>

    <!-- 评分和使用统计 -->
    <div class="stats-section">
      <el-rate v-model="skill.rating" disabled show-score />
      <span>{{ skill.rating_count }} 条评价</span>
      <span>👁️ {{ skill.usage_count }} 次使用</span>
    </div>

    <!-- 功能描述 -->
    <div class="description-section">
      <h2>📝 功能描述</h2>
      <p>{{ skill.description }}</p>

      <!-- 如果有官方文档 -->
      <div v-if="skill.documentation" class="documentation">
        <h3>📖 使用文档</h3>
        <pre>{{ skill.documentation }}</pre>
      </div>
    </div>

    <!-- 立即试用 -->
    <div class="try-section">
      <h2>💬 立即试用 (无需登录)</h2>
      <el-card>
        <el-input
          v-model="trialMessage"
          type="textarea"
          :rows="4"
          placeholder="输入要测试的内容..."
        />
        <el-button
          type="primary"
          :loading="executing"
          @click="trySkill"
          style="margin-top: 10px"
        >
          💬 执行
        </el-button>
      </el-card>

      <!-- 执行结果 -->
      <div v-if="trialResult" class="trial-result">
        <el-alert
          :type="trialResult.status === 'success' ? 'success' : 'error'"
          :title="trialResult.status === 'success' ? '执行成功' : '执行失败'"
          show-icon
          :closable="false"
        >
          <pre>{{ trialResult.output || trialResult.error }}</pre>
        </el-alert>
      </div>
    </div>

    <!-- 创建 Agent -->
    <div class="create-agent-section">
      <h2>🚀 创建我的 Agent</h2>
      <el-card>
        <el-form :model="agentForm" label-width="100px">
          <el-form-item label="Agent 名称">
            <el-input v-model="agentForm.name" placeholder="例如：My Analyzer" />
          </el-form-item>
          <el-form-item label="Agent 类型">
            <el-radio-group v-model="agentForm.agent_type">
              <el-radio label="react">ReAct Agent (推理+行动)</el-radio>
              <el-radio label="progressive">Progressive Agent (渐进式)</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="模型选择">
            <el-select v-model="agentForm.model_name">
              <el-option label="Qwen Max (推荐)" value="qwen-max" />
              <el-option label="Qwen Plus" value="qwen-plus" />
              <el-option label="DeepSeek Chat" value="deepseek-chat" />
            </el-select>
          </el-form-item>
          <el-form-item label="温度">
            <el-slider v-model="agentForm.temperature" :min="0" :max="2" :step="0.1" show-input />
          </el-form-item>
        </el-form>
        <el-button type="primary" @click="createAgent" :loading="creating">
          🚀 一键创建并执行
        </el-button>
      </el-card>
    </div>

    <!-- 使用统计 -->
    <div class="analytics-section">
      <h2>📊 使用统计</h2>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card>
            <div class="stat">
              <div class="stat-value">{{ skill.usage_count }}</div>
              <div class="stat-label">总使用次数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card>
            <div class="stat">
              <div class="stat-value">{{ skill.weekly_usage }}</div>
              <div class="stat-label">本周使用</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card>
            <div class="stat">
              <div class="stat-value">{{ skill.top_user_department }}</div>
              <div class="stat-label">主要用户</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 用户评价 -->
    <div class="reviews-section">
      <h2>💬 用户评价 ({{ skill.reviews.length }})</h2>
      <div class="review-list">
        <div v-for="review in skill.reviews" :key="review.id" class="review-item">
          <el-rate v-model="review.rating" disabled />
          <span class="reviewer">{{ review.reviewer_name }}</span>
          <p class="review-content">{{ review.content }}</p>
        </div>
      </div>
      <el-button v-if="!skill.has_rated" @click="showReviewDialog = true">
        ⭐ 我也要评价
      </el-button>
    </div>

    <!-- 底部操作 -->
    <div class="action-bar">
      <el-button @click="saveSkill">
        💾 保存到我的 Skills
      </el-button>
      <el-button @click="$router.back()">
        🔙 返回
      </el-button>
    </div>
  </div>
</template>
```

---

## 2. Workflow Studio

### 2.1 工作流编辑器

```vue
<template>
  <div class="workflow-studio">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <el-button-group>
        <el-button icon="FolderOpened" @click="showMyWorkflows">📋 我的 Workflows</el-button>
        <el-button icon="Plus" @click="createNewWorkflow">➕ 新建 Workflow</el-button>
        <el-button icon="Document" @click="showTemplates">📚 模板库</el-button>
      </el-button-group>

      <el-button v-if="currentWorkflow" type="primary" @click="saveWorkflow">
        💾 保存
      </el-button>
      <el-button v-if="currentWorkflow" @click="executeWorkflow">
        ▶️ 执行
      </el-button>
    </div>

    <div class="studio-content">
      <!-- 左侧组件库 -->
      <div class="component-library">
        <h3>🧩 拖拽组件</h3>

        <el-collapse v-model="activeComponents">
          <el-collapse-item title="📊 Skills" name="skills">
            <div class="component-list">
              <div
                v-for="skill in availableSkills"
                :key="skill.id"
                class="draggable-component"
                draggable="true"
                @dragstart="onDragStart($event, 'skill', skill)"
              >
                <el-checkbox v-model="skill.selected">{{ skill.name }}</el-checkbox>
              </div>
            </div>
          </el-collapse-item>

          <el-collapse-item title="🤖 Agents" name="agents">
            <div class="component-list">
              <div
                v-for="agent in availableAgents"
                :key="agent.id"
                class="draggable-component"
                draggable="true"
                @dragstart="onDragStart($event, 'agent', agent)"
              >
                <el-checkbox v-model="agent.selected">{{ agent.name }}</el-checkbox>
              </div>
            </div>
          </el-collapse-item>

          <el-collapse-item title="🔶 条件判断" name="conditions">
            <div class="component-list">
              <div
                class="draggable-component"
                draggable="true"
                @dragstart="onDragStart($event, 'condition')"
              >
                🔶 If/Else 条件分支
              </div>
            </div>
          </el-collapse-item>

          <el-collapse-item title="⚙️ 触发器" name="triggers">
            <div class="component-list">
              <div class="trigger-option" @click="addTrigger('schedule')">
                ⏰ 定时触发
              </div>
              <div class="trigger-option" @click="addTrigger('manual')">
                🔔 手动触发
              </div>
              <div class="trigger-option" @click="addTrigger('webhook')">
                🌐 Webhook
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- 中间画布区域 -->
      <div class="canvas-area">
        <div
          v-if="!currentWorkflow"
          class="empty-state"
        >
          <h2>🔧 开始创建您的 Workflow</h2>
          <p>从模板库选择或从零开始</p>
          <el-button type="primary" @click="showTemplates">📚 浏览模板库</el-button>
        </div>

        <div
          v-else
          class="workflow-canvas"
          @drop="onDrop"
          @dragover.prevent
        >
          <!-- Workflow 节点可视化 -->
          <div class="workflow-nodes">
            <div
              v-for="(step, index) in workflowSteps"
              :key="step.id"
              class="workflow-node"
            >
              <div class="node-header">
                <span class="step-number">{{ index + 1 }}</span>
                <span class="step-name">{{ step.name }}</span>
                <el-button
                  icon="Delete"
                  circle
                  size="small"
                  type="danger"
                  @click="removeStep(step.id)"
                />
              </div>
              <div class="node-body">
                <el-tag :type="getStepTypeColor(step.type)">
                  {{ getStepTypeLabel(step.type) }}
                </el-tag>
                <span>{{ step.config.name }}</span>
              </div>
              <div class="node-arrow">↓</div>
            </div>
          </div>

          <!-- 添加节点按钮 -->
          <div class="add-node-section">
            <el-button
              icon="Plus"
              @click="showAddStepDialog"
            >
              ➕ 添加步骤
            </el-button>
          </div>
        </div>
      </div>

      <!-- 右侧配置面板 -->
      <div class="config-panel" v-if="selectedStep">
        <h3>⚙️ 配置: {{ selectedStep.name }}</h3>
        <el-form label-width="100px">
          <!-- 根据步骤类型显示不同的配置项 -->
          <div v-if="selectedStep.type === 'skill'">
            <el-form-item label="Skill">
              <el-select v-model="selectedStep.config.skill_id">
                <el-option
                  v-for="skill in availableSkills"
                  :key="skill.id"
                  :label="skill.name"
                  :value="skill.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="参数配置">
              <el-input
                v-model="selectedStep.config.params"
                type="textarea"
                :rows="5"
                placeholder="JSON 格式的参数配置"
              />
            </el-form-item>
          </div>

          <div v-else-if="selectedStep.type === 'agent'">
            <el-form-item label="Agent">
              <el-select v-model="selectedStep.config.agent_id">
                <el-option
                  v-for="agent in availableAgents"
                  :key="agent.id"
                  :label="agent.name"
                  :value="agent.id"
                />
              </el-select>
            </el-form-item>
          </div>

          <div v-else-if="selectedStep.type === 'condition'">
            <el-form-item label="条件">
              <el-input
                v-model="selectedStep.config.condition"
                placeholder="例如: {{ price_change }} > 0.05"
              />
            </el-form-item>
            <el-form-item label="True 分支">
              <el-select v-model="selectedStep.config.true_branch">
                <el-option label="发送告警" value="send_alert" />
                <el-option label="结束" value="end" />
              </el-select>
            </el-form-item>
          </div>

          <el-form-item label="输出变量">
            <el-input
              v-model="selectedStep.output_to"
              placeholder="变量名"
            />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 添加步骤对话框 -->
    <el-dialog v-model="showAddStep" title="添加工作流步骤" width="600px">
      <el-form :model="newStep" label-width="100px">
        <el-form-item label="步骤名称" required>
          <el-input v-model="newStep.name" placeholder="例如：查询价格" />
        </el-form-item>
        <el-form-item label="步骤类型" required>
          <el-select v-model="newStep.type">
            <el-option label="📊 Skill" value="skill" />
            <el-option label="🤖 Agent" value="agent" />
            <el-option label="🔶 条件判断" value="condition" />
          </el-select>
        </el-form-item>

        <!-- 根据类型显示不同的配置 -->
        <div v-if="newStep.type === 'skill'">
          <el-form-item label="选择 Skill" required>
            <el-select v-model="newStep.skill_id" placeholder="选择 Skill">
              <el-option
                v-for="skill in availableSkills"
                :key="skill.id"
                :label="skill.name"
                :value="skill.id"
              />
            </el-select>
          </el-form-item>
        </div>

        <div v-else-if="newStep.type === 'agent'">
          <el-form-item label="选择 Agent" required>
            <el-select v-model="newStep.agent_id" placeholder="选择 Agent">
              <el-option
                v-for="agent in availableAgents"
                :key="agent.id"
                :label="agent.name"
                :value="agent.id"
              />
            </el-select>
          </el-form-item>
        </div>

        <el-form-item label="输出变量">
          <el-input v-model="newStep.output_to" placeholder="保存结果到变量" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddStep = false">取消</el-button>
        <el-button type="primary" @click="addStep">添加</el-button>
      </template>
    </el-dialog>

    <!-- 执行结果对话框 -->
    <el-dialog v-model="showExecutionResult" title="工作流执行结果" width="800px">
      <div class="execution-result">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="执行状态">
            <el-tag :type="executionResult.status === 'success' ? 'success' : 'danger'">
              {{ executionResult.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ executionResult.started_at }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ executionResult.completed_at }}
          </el-descriptions-item>
          <el-descriptions-item label="执行耗时">
            {{ executionResult.duration }}秒
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <h4>步骤执行详情</h4>
        <el-timeline>
          <el-timeline-item
            v-for="step in executionResult.steps"
            :key="step.id"
            :timestamp="step.completed_at"
            :type="step.status === 'success' ? 'success' : 'danger'"
          >
            <h5>{{ step.name }}</h5>
            <p v-if="step.input"><strong>输入:</strong> {{ step.input }}</p>
            <p v-if="step.output"><strong>输出:</strong> {{ step.output }}</p>
            <p v-if="step.error" class="error"><strong>错误:</strong> {{ step.error }}</p>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-dialog>
  </div>
</template>
```

---

## 3. 团队空间

### 3.1 团队主页

```vue
<template>
  <div class="team-space">
    <!-- 部门选择 -->
    <div class="department-selector">
      <el-select v-model="selectedDepartment" placeholder="选择部门">
        <el-option label="研发部" value="研发部" />
        <el-option label="市场部" value="市场部" />
        <el-option label="客服部" value="客服部" />
        <el-option label="IT 部" value="IT 部" />
      </el-select>
    </div>

    <!-- 团队成员 -->
    <div class="team-members">
      <h2>👥 团队成员 ({{ teamMembers.length }})</h2>
      <el-button type="primary" size="small" @click="inviteMember">
        ➕ 邀请成员
      </el-button>

      <el-row :gutter="20">
        <el-col :span="4" v-for="member in teamMembers" :key="member.id">
          <el-card class="member-card">
            <div class="member-avatar">
              {{ member.username.charAt(0).toUpperCase() }}
            </div>
            <div class="member-name">{{ member.username }}</div>
            <div class="member-role">{{ getRoleLabel(member.role) }}</div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 团队资源 -->
    <el-tabs v-model="activeResourceTab">
      <!-- 团队 Skills -->
      <el-tab-pane label="📦 团队 Skills" name="skills">
        <div class="resource-toolbar">
          <el-button type="primary" @click="uploadSkill">
            ➕ 上传 Skill
          </el-button>
          <el-input
            v-model="skillSearch"
            placeholder="搜索 Skills..."
            prefix-icon="Search"
            style="width: 300px"
          />
        </div>

        <el-table :data="teamSkills" stripe>
          <el-table-column prop="name" label="Skill 名称" />
          <el-table-column prop="created_by" label="创建者" width="120" />
          <el-table-column prop="usage_count" label="使用次数" width="100" />
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button link type="primary" @click="useSkill(row)">使用</el-button>
              <el-button link type="primary" @click="editSkill(row)">编辑</el-button>
              <el-button link type="danger" @click="deleteSkill(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 团队 Agents -->
      <el-tab-pane label="🤖 团队 Agents" name="agents">
        <div class="resource-toolbar">
          <el-button type="primary" @click="createAgent">
            ➕ 创建 Agent
          </el-button>
        </div>

        <el-table :data="teamAgents" stripe>
          <el-table-column prop="name" label="Agent 名称" />
          <el-table-column prop="model_name" label="模型" width="150" />
          <el-table-column prop="usage_count" label="使用次数" width="100" />
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button link type="primary" @click="executeAgent(row)">执行</el-button>
              <el-button link type="primary" @click="viewAgent(row)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 团队 Workflows -->
      <el-tab-pane label="🔧 团队 Workflows" name="workflows">
        <div class="resource-toolbar">
          <el-button type="primary" @click="createWorkflow">
            ➕ 创建 Workflow
          </el-button>
        </div>

        <el-table :data="teamWorkflows" stripe>
          <el-table-column prop="name" label="Workflow 名称" />
          <el-table-column prop="trigger_type" label="触发类型" width="120" />
          <el-table-column prop="last_run" label="最后执行" width="180" />
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button link type="primary" @click="executeWorkflow(row)">执行</el-button>
              <el-button link type="primary" @click="editWorkflow(row)">编辑</el-button>
              <el-button link type="primary" @click="viewHistory(row)">历史</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 团队统计 -->
    <div class="team-stats">
      <h2>📊 团队统计</h2>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-value">{{ stats.active_members }}/{{ stats.total_members }}</div>
            <div class="stat-label">本月活跃成员</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-value">{{ stats.new_skills_this_month }}</div>
            <div class="stat-label">本月新增 Skills</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-value">{{ stats.execution_count_this_month }}</div>
            <div class="stat-label">本月执行次数</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-value">{{ stats.tokens_saved }}</div>
            <div class="stat-label">节省 Tokens</div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>
```

---

## 4. 智能推荐系统

```vue
<template>
  <div class="recommendations">
    <h2>💡 为您推荐</h2>
    <p class="subtitle">基于您的使用习惯和团队动态智能推荐</p>

    <!-- 推荐的 Skills -->
    <div class="recommendation-section">
      <h3>🎯 推荐 Skills</h3>
      <el-row :gutter="20">
        <el-col :span="12" v-for="item in recommendedSkills" :key="item.id">
          <el-card class="recommendation-card">
            <div class="card-header">
              <span class="card-title">{{ item.skill.name }}</span>
              <el-tag size="small">{{ item.reason }}</el-tag>
            </div>
            <p class="card-reason">{{ item.description }}</p>
            <el-button type="primary" @click="useRecommendedSkill(item.skill)">
              🚀 一键创建 Agent
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 推荐的 Workflows -->
    <div class="recommendation-section">
      <h3>🎯 推荐 Workflow</h3>
      <el-row :gutter="20">
        <el-col :span="12" v-for="item in recommendedWorkflows" :key="item.id">
          <el-card class="recommendation-card workflow-card">
            <div class="card-header">
              <span class="card-title">{{ item.workflow.name }}</span>
              <el-tag type="success" size="small">🔥 热门</el-tag>
            </div>
            <p class="card-description">{{ item.description }}</p>
            <div class="workflow-info">
              <span>📦 组合 {{ item.skill_count }} 个 Skills</span>
              <span>👁️ {{ item.usage_count }} 次复用</span>
            </div>
            <el-button @click="useRecommendedWorkflow(item.workflow)">
              🚀 一键复用
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-button @click="refreshRecommendations">
      🔄 刷新推荐
    </el-button>
    <el-button @click="viewMore">
      📊 查看更多
    </el-button>
  </div>
</template>
```

---

## 5. 游戏化系统

### 5.1 用户等级与成就

```vue
<template>
  <div class="gamification">
    <!-- 用户等级 -->
    <div class="user-level">
      <h2>🏆 我的等级</h2>
      <div class="level-info">
        <div class="level-badge">
          <span class="level-stars">⭐⭐⭐⭐☆</span>
          <span class="level-name">Expert User</span>
        </div>
        <div class="level-bar">
          <el-progress
            :percentage="75"
            :format="() => '3,450 / 4,000 XP'"
            :stroke-width="20"
          />
          <p class="level-progress">还需 550 XP 升级到 Master User</p>
        </div>
      </div>

      <!-- 经验获取途径 -->
      <div class="xp-sources">
        <h4>获取经验值：</h4>
        <ul>
          <li>✅ 执行 Agent (+10 XP)</li>
          <li>✅ 创建 Workflow (+50 XP)</li>
          <li>✅ 分享 Skill (+150 XP)</li>
          <li>⭐ 获得好评 (+20 XP)</li>
        </ul>
      </div>
    </div>

    <!-- 徽章 -->
    <div class="badges">
      <h2>🎖️ 我的徽章</h2>
      <el-row :gutter="15">
        <el-col :span="6" v-for="badge in badges" :key="badge.id">
          <el-card class="badge-card" :class="{ earned: badge.earned }">
            <div class="badge-icon">{{ badge.icon }}</div>
            <div class="badge-name">{{ badge.name }}</div>
            <div class="badge-description">{{ badge.description }}</div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 排行榜 -->
    <div class="leaderboard">
      <h2>🏆 本周排行榜</h2>
      <el-tabs v-model="leaderboardType">
        <el-tab-pane label="经验值排行" name="xp">
          <el-table :data="xpLeaderboard" stripe>
            <el-table-column label="排名" width="80">
              <template #default="{ $index }">
                <span class="rank-badge" :class="{ top3: $index < 3 }">
                  {{ $index + 1 }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="username" label="用户" />
            <el-table-column prop="xp" label="经验值" width="120" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="贡献度排行" name="contribution">
          <el-table :data="contributionLeaderboard" stripe>
            <el-table-column label="排名" width="80" />
            <el-table-column prop="username" label="用户" />
            <el-table-column prop="skill_count" label="Skills" width="100" />
            <el-table-column prop="usage_count" label="使用次数" width="120" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>
```

---

## 6. 路由结构更新

```typescript
// router/index.ts
const routes: RouteRecordRaw[] = [
  // 公共路由
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false }
  },

  // 主布局路由
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
      },

      // Skills Marketplace
      {
        path: 'marketplace',
        name: 'SkillsMarketplace',
        component: () => import('@/views/MarketplaceView.vue'),
      },
      {
        path: 'marketplace/skill/:id',
        name: 'SkillDetail',
        component: () => import('@/views/SkillDetailView.vue'),
      },
      {
        path: 'marketplace/my-skills',
        name: 'MySkills',
        component: () => import('@/views/MySkillsView.vue'),
      },

      // Skills 管理
      {
        path: 'skills',
        name: 'Skills',
        component: () => import('@/views/SkillsView.vue'),
      },

      // Agents 管理
      {
        path: 'agents',
        name: 'Agents',
        component: () => import('@/views/AgentsView.vue'),
      },
      {
        path: 'agents/:id',
        name: 'AgentDetail',
        component: () => import('@/views/AgentDetailView.vue'),
      },

      // Workflow Studio
      {
        path: 'workflows',
        name: 'Workflows',
        component: () => import('@/views/WorkflowsView.vue'),
      },
      {
        path: 'workflows/create',
        name: 'CreateWorkflow',
        component: () => import('@/views/CreateWorkflowView.vue'),
      },
      {
        path: 'workflows/:id',
        name: 'WorkflowDetail',
        component: () => import('@/views/WorkflowDetailView.vue),
      },
      {
        path: 'workflows/:id/edit',
        name: 'EditWorkflow',
        component: () => import('@/views/EditWorkflowView.vue'),
      },

      // 团队空间
      {
        path: 'team',
        name: 'TeamSpace',
        component: () => import('@/views/TeamView.vue'),
      },

      // 监控数据
      {
        path: 'monitoring',
        name: 'Monitoring',
        component: () => import('@/views/MonitoringView.vue'),
      },

      // 成就系统
      {
        path: 'achievements',
        name: 'Achievements',
        component: () => import('@/views/AchievementsView.vue'),
      },

      // 用户设置
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/SettingsView.vue'),
      },
    ],
  },
]
```

---

## 7. API 接口设计

### Skills Marketplace API

```python
@router.get("/marketplace/skills", response_model=List[SkillMarketResponse])
async def get_marketplace_skills(
    category: Optional[str] = None,
    sharing_scope: Optional[str] = None,
    sort_by: str = "usage_count",
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取 Marketplace Skills 列表

    - 支持分类筛选
    - 支持权限过滤（个人/团队/全局）
    - 支持排序（热度、最新、评分）
    """
    query = db.query(Skill).filter(Skill.is_active == True)

    # 权限过滤
    if sharing_scope == "private":
        query = query.filter(Skill.created_by == current_user.id)
    elif sharing_scope == "team":
        query = query.filter(
            (Skill.created_by == current_user.id) |
            (Skill.sharing_scope == "team") &
            (Skill.created_by_department == current_user.department)
        )
    # public 无限制

    # 分类筛选
    if category:
        query = query.filter(Skill.category == category)

    # 排序
    if sort_by == "usage_count":
        query = query.order_by(Skill.usage_count.desc())
    elif sort_by == "rating":
        query = query.order_by(Skill.rating.desc())
    elif sort_by == "newest":
        query = query.order_by(Skill.created_at.desc())

    skills = query.offset(skip).limit(limit).all()
    return [SkillMarketResponse.model_validate(s) for s in skills]


@router.post("/marketplace/skills/{skill_id}/try", response_model=TrySkillResponse)
async def try_skill(
    skill_id: int,
    request: TrySkillRequest,
    db: Session = Depends(get_db),
):
    """
    试用 Skill（无需登录）

    - 使用公共 Agent 执行 Skill
    - 返回执行结果
    - 消耗 tokens
    """
    skill = db.query(Skill).get(skill_id)

    # 执行 Skill
    result = await execute_skill(skill, request.message)

    # 增加使用计数
    skill.usage_count += 1
    db.commit()

    return result


@router.post("/marketplace/skills/{skill_id}/create-agent", response_model=AgentResponse)
async def create_agent_from_skill(
    skill_id: int,
    config: CreateAgentFromSkillRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    从 Skill 一键创建 Agent

    - 自动配置 Skill
    - 使用推荐的参数
    """
    skill = db.query(Skill).get(skill_id)

    agent = Agent(
        name=config.name or f"{skill.name} Agent",
        description=config.description or f"基于 {skill.name} 的 Agent",
        model_name=config.model_name or "qwen-max",
        temperature=config.temperature or 0.7,
        system_prompt=config.system_prompt,
        created_by=current_user.id,
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)

    # 关联 Skill
    agent_skill = AgentSkill(
        agent_id=agent.id,
        skill_id=skill.id,
        enabled=True,
    )
    db.add(agent_skill)
    db.commit()

    return AgentResponse.model_validate(agent)


@router.post("/marketplace/skills/{skill_id}/rate", response_model=RatingResponse)
async def rate_skill(
    skill_id: int,
    rating: int,
    comment: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    评价 Skill

    - 1-5 星评分
    - 支持评论
    - 更新 Skill 的平均评分
    """
    # 检查是否已评价
    existing = db.query(SkillRating).filter(
        skill_id == skill_id,
        user_id == current_user.id
    ).first()

    if existing:
        # 更新评价
        existing.rating = rating
        existing.comment = comment
    else:
        # 创建新评价
        new_rating = SkillRating(
            skill_id=skill_id,
            user_id=current_user.id,
            rating=rating,
            comment=comment,
        )
        db.add(new_rating)

    db.commit()

    # 更新 Skill 的平均评分
    skill = db.query(Skill).get(skill_id)
    ratings = db.query(SkillRating).filter(SkillRating.skill_id == skill_id).all()
    skill.rating = sum(r.rating for r in ratings) / len(ratings)
    skill.rating_count = len(ratings)

    db.commit()

    return {"message": "评价成功", "new_rating": skill.rating}


@router.post("/marketplace/skills/{skill_id}/save")
async def save_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    保存 Skill 到我的收藏
    """
    existing = db.query(SavedSkill).filter(
        skill_id == skill_id,
        user_id == current_user.id
    ).first()

    if not existing:
        saved = SavedSkill(
            skill_id=skill_id,
            user_id=current_user.id,
        )
        db.add(saved)
        db.commit()

    return {"message": "已保存到我的 Skills"}
```

---

## 8. 数据库模型

```python
# Skill 增强
class Skill(Base):
    existing_fields...

    # 权限字段
    sharing_scope: Mapped[str] = mapped_column(
        String(20),
        default="private",  # private, team, public
        nullable=False
    )
    department: Mapped[Optional[str]] = mapped_column(String(50))
    created_by_department: Mapped[Optional[str]] = mapped_column(String(50))
    is_official: Mapped[bool] = mapped_column(Boolean, default=False)

    # 统计字段
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    weekly_usage: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[Optional[float]] = mapped_column(DECIMAL(3, 2))
    rating_count: Mapped[int] = mapped_column(Integer, default=0)

    # 文档
    description: Mapped[Optional[str]] = mapped_column(Text)
    documentation: Mapped[Optional[str]] = mapped_column(Text)


# Skill 评价
class SkillRating(Base):
    __tablename__ = "skill_ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(Integer)  # 1-5
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # 关系
    skill = relationship("Skill", backref="ratings")
    user = relationship("User")


# 保存的 Skills
class SavedSkill(Base):
    __tablename__ = "saved_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime.utcnow)


# Workflow
class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    sharing_scope: Mapped[str] = mapped_column(String(20), default="private")

    # 工作流配置
    config: Mapped[dict] = mapped_column(JSON)  # Workflow 定义

    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # 关系
    creator = relationship("User")
    executions = relationship("WorkflowExecution", back_populates="workflow")


# Workflow 执行记录
class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workflow_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflows.id"))

    status: Mapped[str] = mapped_column(String(20), default="pending")
    input_data: Mapped[dict] = mapped_column(JSON)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    started_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    completed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    # 关系
    workflow = relationship("Workflow", back_populates="executions")
    steps = relationship("WorkflowStepExecution", back_populates="execution")


# Workflow 步骤执行记录
class WorkflowStepExecution(Base):
    __tablename__ = "workflow_step_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    execution_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflow_executions.id"))

    step_name: Mapped[str] = mapped_column(String(100))
    step_type: Mapped[str] = mapped_column(String(20))  # skill, agent, condition
    skill_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("skills.id"))
    agent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("agents.id"))

    status: Mapped[str] = mapped_column(String(20))
    input_data: Mapped[Optional[dict]] = mapped_column(JSON)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    started_at: Mapped[DateTime] = mapped_column(DateTime)
    completed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)


# 用户增强
class User(Base):
    existing_fields...

    # 新增字段
    department: Mapped[Optional[str]] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(20), default="user")  # user, admin, super_admin

    # 统计
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[str] = mapped_column(String(20), default="beginner")

    # 关系
    saved_skills = relationship("SavedSkill", back_populates="user")
    ratings = relationship("SkillRating", back_populates="user")


# 成就系统
class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str] = mapped_column(String(50))  # emoji
    description: Mapped[str] = mapped_column(Text)
    requirement: Mapped[dict] = mapped_column(JSON)  # 获得条件

    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime.utcnow)


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    achievement_id: Mapped[int] = mapped_column(Integer, ForeignKey("achievements.id"))
    earned_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
```

---

## 9. 使用示例

### 示例 1：用户浏览 Marketplace

```typescript
// 用户流程
1. 登录平台 → 首页看到推荐 Skills
2. 点击热门 Skill → 进入详情页
3. "立即试用" → 输入测试内容 → 看到结果
4. 满意 → "创建 Agent" → 自动配置
5. "保存到我的 Skills" → 方便下次使用
```

### 示例 2：创建 Workflow

```typescript
// 用户流程
1. 进入 Workflow Studio
2. 选择"价格监控模板" → 一键复用
3. 拖拽调整：添加额外的邮件通知步骤
4. 配置参数：设置阈值为 5%
5. "保存" → 设置定时触发（每天早上 8 点）
6. "执行" → 查看结果 → 确认正常运行
```

### 示例 3：团队协作

```typescript
// 用户流程
1. 进入"团队空间"
2. 上传自己开发的 Skill
3. 设置共享范围为"团队"
4. 团队成员浏览 → "一键创建 Agent"
5. 大家都使用同一个 Skill → 提高效率
6. 查看团队统计 → 了解使用情况
```

---

## 10. 核心价值

| 功能 | 用户价值 | 商业价值 |
|------|---------|---------|
| **Skills Marketplace** | 快速找到需要的技能 | 提高 Skills 利用率 |
| **One-Click Agent** | 3 秒创建 Agent | 降低使用门槛 |
| **Workflow Studio** | 可视化编排复杂流程 | 提升平台粘性 |
| **模板库** | 一键复用最佳实践 | 知识沉淀 |
| **智能推荐** | 发现相关能力 | 提高活跃度 |
| **团队协作** | 共享资源，提升效率 | 企业级应用 |
| **游戏化** | 激励参与和贡献 | 社区活跃 |

---

这个设计文档完整地规划了 LingNexus Platform 的前端功能架构。接下来可以开始实施！
