# 应用构建器前端设计方案

可视化低代码应用搭建系统的前端设计

## 核心设计理念

**3 分钟搭建一个业务系统**：
1. 选择模板（CRM、任务管理、库存管理...）
2. 连接数据源（用户的数据表）
3. 配置页面布局（拖拽组件）
4. 调整样式和交互
5. 发布应用

## 整体架构

```
应用构建器
│
├── 左侧面板：组件库
│   ├── 基础组件
│   │   ├── 表格（Table）
│   │   ├── 表单（Form）
│   │   ├── 详情页（Detail）
│   │   └── 列表（List）
│   ├── 布局组件
│   │   ├── 容器（Container）
│   │   ├── 标签页（Tabs）
│   │   ├── 折叠面板（Collapse）
│   │   └── 分栏（Row/Col）
│   └── 数据组件
│       ├── 图表（Chart）
│       ├── 统计卡片（Statistic）
│       └── 仪表盘（Dashboard）
│
├── 中间画布：页面编辑器
│   ├── 拖拽区域
│   ├── 组件渲染
│   ├── 选中状态
│   └── 连接线（数据流）
│
└── 右侧面板：属性配置
    ├── 组件属性
    ├── 数据绑定
    ├── 样式配置
    ├── 交互设置
    └── 权限控制
```

## 页面布局设计

### 1. 应用构建器主界面

```vue
<template>
  <div class="app-builder">
    <!-- 顶部工具栏 -->
    <div class="builder-header">
      <div class="header-left">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-divider direction="vertical" />
        <el-input
          v-model="app.app_name"
          placeholder="应用名称"
          size="large"
          style="width: 200px"
        />
      </div>

      <div class="header-center">
        <el-radio-group v-model="currentView">
          <el-radio-button label="pages">页面</el-radio-button>
          <el-radio-button label="navigation">导航</el-radio-button>
          <el-radio-button label="theme">主题</el-radio-button>
        </el-radio-group>
      </div>

      <div class="header-right">
        <el-button @click="saveDraft">
          <el-icon><DocumentCopy /></el-icon>
          保存草稿
        </el-button>
        <el-button @click="previewApp">
          <el-icon><View /></el-icon>
          预览
        </el-button>
        <el-button type="primary" @click="publishApp">
          <el-icon><Promotion /></el-icon>
          发布
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="builder-content">
      <!-- 左侧面板 -->
      <div class="left-panel">
        <ComponentLibrary
          :components="componentLibrary"
          @drag-start="onComponentDragStart"
        />
      </div>

      <!-- 中间画布 -->
      <div class="canvas-container">
        <!-- 页面列表 -->
        <div class="page-tabs" v-if="currentView === 'pages'">
          <el-tabs
            v-model="currentPageId"
            type="card"
            closable
            @tab-remove="removePage"
            @tab-add="addPage"
          >
            <el-tab-pane
              v-for="page in pages"
              :key="page.id"
              :label="page.name"
              :name="page.id"
            >
              <!-- 页面画布 -->
              <PageCanvas
                :page="page"
                :components="pageComponents"
                :selected-component="selectedComponent"
                @select="onSelectComponent"
                @update="onUpdateComponent"
                @drop="onComponentDrop"
              />
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 导航配置 -->
        <div class="navigation-config" v-else-if="currentView === 'navigation'">
          <NavigationConfig
            :navigation="app.config.navigation"
            :pages="pages"
            @update="onUpdateNavigation"
          />
        </div>

        <!-- 主题配置 -->
        <div class="theme-config" v-else-if="currentView === 'theme'">
          <ThemeConfig
            :theme="app.config.theme"
            @update="onUpdateTheme"
          />
        </div>
      </div>

      <!-- 右侧面板 -->
      <div class="right-panel">
        <ComponentProperties
          v-if="selectedComponent"
          :component="selectedComponent"
          :data-sources="dataSources"
          @update="onUpdateProperty"
        />
        <PageProperties
          v-else-if="selectedPage"
          :page="selectedPage"
          @update="onUpdatePageProperty"
        />
        <EmptyState v-else message="选择组件或页面以配置属性" />
      </div>
    </div>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="应用预览"
      width="90%"
      fullscreen
    >
      <AppPreview :app="app" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAppBuilder } from '@/composables/useAppBuilder'

const {
  app,
  pages,
  currentView,
  currentPageId,
  selectedComponent,
  componentLibrary,
  dataSources,
  saveDraft,
  publishApp
} = useAppBuilder()

const selectedPage = computed(() =>
  pages.value.find(p => p.id === currentPageId.value)
)

function onComponentDragStart(component) {
  // 开始拖拽组件
}

function onComponentDrop(component, position) {
  // 在画布上放置组件
}
</script>

<style scoped>
.app-builder {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.builder-header {
  height: 60px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: #fff;
}

.builder-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.left-panel {
  width: 280px;
  border-right: 1px solid #e0e0e0;
  background: #f5f7fa;
}

.canvas-container {
  flex: 1;
  background: #f0f2f5;
  overflow: auto;
}

.right-panel {
  width: 320px;
  border-left: 1px solid #e0e0e0;
  background: #f5f7fa;
  overflow-y: auto;
}
</style>
```

### 2. 组件库（左侧面板）

```vue
<template>
  <div class="component-library">
    <!-- 搜索框 -->
    <div class="search-box">
      <el-input
        v-model="searchQuery"
        placeholder="搜索组件..."
        prefix-icon="Search"
        clearable
      />
    </div>

    <!-- 组件分类 -->
    <el-collapse v-model="activeCategories" accordion>
      <!-- 基础组件 -->
      <el-collapse-item title="基础组件" name="basic">
        <div class="component-list">
          <div
            v-for="component in basicComponents"
            :key="component.type"
            class="component-item"
            draggable="true"
            @dragstart="$emit('drag-start', component)"
          >
            <div class="component-icon">
              <el-icon :size="24">
                <component :is="component.icon" />
              </el-icon>
            </div>
            <div class="component-info">
              <div class="component-name">{{ component.name }}</div>
              <div class="component-desc">{{ component.description }}</div>
            </div>
          </div>
        </div>
      </el-collapse-item>

      <!-- 数据组件 -->
      <el-collapse-item title="数据组件" name="data">
        <div class="component-list">
          <div
            v-for="component in dataComponents"
            :key="component.type"
            class="component-item"
            draggable="true"
            @dragstart="$emit('drag-start', component)"
          >
            <div class="component-icon">
              <el-icon :size="24" color="#409EFF">
                <component :is="component.icon" />
              </el-icon>
            </div>
            <div class="component-info">
              <div class="component-name">{{ component.name }}</div>
              <div class="component-desc">{{ component.description }}</div>
            </div>
            <el-tag size="small" type="info">需要数据源</el-tag>
          </div>
        </div>
      </el-collapse-item>

      <!-- 布局组件 -->
      <el-collapse-item title="布局组件" name="layout">
        <div class="component-list">
          <div
            v-for="component in layoutComponents"
            :key="component.type"
            class="component-item"
            draggable="true"
            @dragstart="$emit('drag-start', component)"
          >
            <div class="component-icon">
              <el-icon :size="24" color="#67C23A">
                <component :is="component.icon" />
              </el-icon>
            </div>
            <div class="component-info">
              <div class="component-name">{{ component.name }}</div>
              <div class="component-desc">{{ component.description }}</div>
            </div>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const searchQuery = ref('')
const activeCategories = ref(['basic'])

// 基础组件
const basicComponents = [
  {
    type: 'table',
    name: '表格',
    description: '展示数据列表',
    icon: 'Grid',
    category: 'basic',
    defaultProps: {
      columns: [],
      pagination: true,
      selectable: true
    }
  },
  {
    type: 'form',
    name: '表单',
    description: '数据录入表单',
    icon: 'Edit',
    category: 'basic',
    defaultProps: {
      fields: [],
      labelWidth: '100px',
      submitButton: true
    }
  },
  {
    type: 'detail',
    name: '详情页',
    description: '数据详情展示',
    icon: 'Document',
    category: 'basic',
    defaultProps: {
      fields: [],
      layout: 'vertical'
    }
  },
  {
    type: 'list',
    name: '列表',
    description: '卡片式列表',
    icon: 'List',
    category: 'basic',
    defaultProps: {
      itemTemplate: {},
      gridSize: 3
    }
  }
]

// 数据组件
const dataComponents = [
  {
    type: 'chart',
    name: '图表',
    description: '数据可视化',
    icon: 'TrendCharts',
    category: 'data',
    defaultProps: {
      chartType: 'line',
      xAxis: '',
      yAxis: []
    }
  },
  {
    type: 'statistic',
    name: '统计卡片',
    description: '关键指标展示',
    icon: 'DataAnalysis',
    category: 'data',
    defaultProps: {
      title: '',
      value: '',
      prefix: '',
      suffix: ''
    }
  },
  {
    type: 'progress',
    name: '进度条',
    description: '任务进度',
    icon: 'Histogram',
    category: 'data',
    defaultProps: {
      field: '',
      showPercentage: true
    }
  }
]

// 布局组件
const layoutComponents = [
  {
    type: 'container',
    name: '容器',
    description: '包含其他组件',
    icon: 'Box',
    category: 'layout',
    defaultProps: {
      padding: '20px',
      background: '#fff'
    }
  },
  {
    type: 'tabs',
    name: '标签页',
    description: '分页展示内容',
    icon: 'Files',
    category: 'layout',
    defaultProps: {
      tabPosition: 'top',
      animated: true
    }
  },
  {
    type: 'divider',
    name: '分割线',
    description: '内容分隔',
    icon: 'Minus',
    category: 'layout',
    defaultProps: {
      direction: 'horizontal',
      contentPosition: 'center'
    }
  }
]
</script>

<style scoped>
.component-library {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.search-box {
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.component-list {
  padding: 8px 0;
}

.component-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin: 4px 8px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: move;
  transition: all 0.2s;
}

.component-item:hover {
  border-color: #409EFF;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.component-icon {
  margin-right: 12px;
}

.component-info {
  flex: 1;
}

.component-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.component-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
</style>
```

### 3. 页面画布（中间编辑区）

```vue
<template>
  <div
    class="page-canvas"
    @drop="onDrop"
    @dragover.prevent
    @dragenter.prevent
  >
    <!-- 画布工具栏 -->
    <div class="canvas-toolbar">
      <el-button-group>
        <el-button size="small" @click="undo">
          <el-icon><RefreshLeft /></el-icon>
          撤销
        </el-button>
        <el-button size="small" @click="redo">
          <el-icon><RefreshRight /></el-icon>
          重做
        </el-button>
      </el-button-group>

      <el-divider direction="vertical" />

      <el-button-group>
        <el-button size="small" @click="addComponent('container')">
          <el-icon><Plus /></el-icon>
          添加容器
        </el-button>
        <el-button size="small" @click="addText">
          <el-icon><Document /></el-icon>
          添加文本
        </el-button>
      </el-button-group>

      <el-divider direction="vertical" />

      <!-- 视图切换 -->
      <el-radio-group v-model="viewMode" size="small">
        <el-radio-button label="design">设计</el-radio-button>
        <el-radio-button label="preview">预览</el-radio-button>
      </el-radio-group>

      <div style="flex: 1"></div>

      <!-- 缩放控制 -->
      <el-button-group size="small">
        <el-button @click="zoomOut">
          <el-icon><ZoomOut /></el-icon>
        </el-button>
        <el-button disabled>{{ Math.round(zoom * 100) }}%</el-button>
        <el-button @click="zoomIn">
          <el-icon><ZoomIn /></el-icon>
        </el-button>
      </el-button-group>
    </div>

    <!-- 画布内容 -->
    <div
      class="canvas-content"
      :style="{
        transform: `scale(${zoom})`,
        transformOrigin: 'top left'
      }"
    >
      <!-- 设计模式 -->
      <div v-if="viewMode === 'design'" class="design-mode">
        <!-- 渲染组件 -->
        <div
          v-for="component in sortedComponents"
          :key="component.id"
          class="canvas-component"
          :class="{
            selected: component.id === selectedComponentId,
            'is-container': isContainer(component.type)
          }"
          :style="getComponentStyle(component)"
          @click.stop="selectComponent(component)"
        >
          <!-- 组件包装器（显示边框和控制点） -->
          <ComponentWrapper
            :component="component"
            :data-sources="dataSources"
            :is-selected="component.id === selectedComponentId"
            @update="onUpdateComponent"
            @delete="onDeleteComponent"
            @duplicate="onDuplicateComponent"
          >
            <!-- 实际组件渲染 -->
            <ComponentRenderer
              :type="component.type"
              :props="component.props"
              :data-source="component.dataSource"
              :children="component.children"
            />
          </ComponentWrapper>

          <!-- 子组件插槽 -->
          <template v-if="isContainer(component.type)">
            <DropZone
              v-if="!component.children || component.children.length === 0"
              @drop="onDropToContainer(component, $event)"
            >
              <el-icon><Plus /></el-icon>
              <span>拖拽组件到这里</span>
            </DropZone>
            <template v-else>
              <CanvasComponent
                v-for="child in component.children"
                :key="child.id"
                :component="child"
                :data-sources="dataSources"
                :selected-component-id="selectedComponentId"
                @select="$emit('select', $event)"
                @update="$emit('update', $event)"
              />
            </template>
          </template>
        </div>

        <!-- 空状态 -->
        <div v-if="components.length === 0" class="empty-canvas">
          <el-result icon="info" title="空页面" sub-title="从左侧拖拽组件到此处开始构建">
            <template #extra>
              <el-button type="primary" @click="useTemplate">
                使用模板
              </el-button>
            </template>
          </el-result>
        </div>
      </div>

      <!-- 预览模式 -->
      <div v-else class="preview-mode">
        <ComponentRenderer
          v-for="component in components"
          :key="component.id"
          :type="component.type"
          :props="component.props"
          :data-source="component.dataSource"
          :children="component.children"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Sortable } from 'sortablejs'

const props = defineProps({
  page: Object,
  components: Array,
  selectedComponent: Object,
  dataSources: Array
})

const emit = defineEmits(['select', 'update', 'delete', 'duplicate'])

const viewMode = ref('design')
const zoom = ref(1)

const selectedComponentId = computed(() => props.selectedComponent?.id)

const sortedComponents = computed(() => {
  return [...props.components].sort((a, b) => a.order - b.order)
})

function getComponentStyle(component) {
  return {
    position: 'absolute',
    left: component.x + 'px',
    top: component.y + 'px',
    width: component.width + 'px',
    minHeight: component.minHeight + 'px',
    zIndex: component.zIndex || 1
  }
}

function isContainer(type) {
  return ['container', 'tabs', 'collapse'].includes(type)
}

function onDrop(event) {
  event.preventDefault()

  const componentType = event.dataTransfer.getData('componentType')
  if (!componentType) return

  // 在画布上创建新组件
  const newComponent = {
    id: `comp_${Date.now()}`,
    type: componentType,
    x: event.offsetX,
    y: event.offsetY,
    width: 400,
    height: 300,
    zIndex: 1,
    props: {},
    children: []
  }

  emit('update', {
    type: 'add',
    component: newComponent
  })
}

function selectComponent(component) {
  emit('select', component)
}

function onUpdateComponent(update) {
  emit('update', update)
}

function onDeleteComponent() {
  emit('delete', props.selectedComponent)
}

function zoomIn() {
  zoom.value = Math.min(zoom.value + 0.1, 2)
}

function zoomOut() {
  zoom.value = Math.max(zoom.value - 0.1, 0.5)
}
</script>

<style scoped>
.page-canvas {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

.canvas-toolbar {
  height: 48px;
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  padding: 0 16px;
  gap: 8px;
}

.canvas-content {
  flex: 1;
  min-height: 800px;
  position: relative;
  overflow: auto;
  padding: 20px;
}

.design-mode {
  position: relative;
  min-height: 800px;
}

.canvas-component {
  position: absolute;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}

.canvas-component:hover {
  border-color: #409EFF;
}

.canvas-component.selected {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.canvas-component.is-container {
  background: rgba(64, 158, 255, 0.05);
  border-style: dashed;
}

.empty-canvas {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 600px;
}
</style>
```

### 4. 属性配置面板（右侧）

```vue
<template>
  <div class="component-properties">
    <!-- 组件标题 -->
    <div class="panel-header">
      <el-icon :size="20" :color="component.color">
        <component :is="getComponentIcon(component.type)" />
      </el-icon>
      <span class="component-name">{{ getComponentName(component.type) }}</span>
    </div>

    <el-divider />

    <!-- 属性选项卡 -->
    <el-tabs v-model="activeTab" stretch>
      <!-- 基本属性 -->
      <el-tab-pane label="属性" name="properties">
        <div class="property-section">
          <!-- 布局属性 -->
          <div class="property-group">
            <div class="group-title">布局</div>

            <el-form label-position="left" label-width="80px" size="small">
              <el-form-item label="宽度">
                <el-input-number
                  v-model="component.width"
                  :min="100"
                  :max="1200"
                  :step="50"
                  controls-position="right"
                  @change="updateProperty('width', $event)"
                />
              </el-form-item>

              <el-form-item label="高度">
                <el-select
                  v-model="component.height"
                  @change="updateProperty('height', $event)"
                >
                  <el-option label="自动" value="auto" />
                  <el-option label="100px" :value="100" />
                  <el-option label="200px" :value="200" />
                  <el-option label="300px" :value="300" />
                  <el-option label="500px" :value="500" />
                  <el-option label="自定义" :value="custom" />
                </el-select>
              </el-form-item>

              <el-form-item label="边距">
                <el-input
                  v-model="component.padding"
                  placeholder="例如: 20px"
                  @change="updateProperty('padding', $event)"
                />
              </el-form-item>
            </el-form>
          </div>

          <!-- 组件特定属性 -->
          <div class="property-group">
            <div class="group-title">{{ getComponentSpecificTitle(component.type) }}</div>

            <!-- 表格组件属性 -->
            <template v-if="component.type === 'table'">
              <TableProperties
                :component="component"
                :data-sources="dataSources"
                @update="updateProperty"
              />
            </template>

            <!-- 表单组件属性 -->
            <template v-else-if="component.type === 'form'">
              <FormProperties
                :component="component"
                :data-sources="dataSources"
                @update="updateProperty"
              />
            </template>

            <!-- 图表组件属性 -->
            <template v-else-if="component.type === 'chart'">
              <ChartProperties
                :component="component"
                :data-sources="dataSources"
                @update="updateProperty"
              />
            </template>
          </div>
        </div>
      </el-tab-pane>

      <!-- 数据绑定 -->
      <el-tab-pane label="数据" name="data">
        <div class="property-section">
          <!-- 数据源选择 -->
          <div class="property-group">
            <div class="group-title">数据源</div>

            <el-select
              v-model="component.dataSource.table"
              placeholder="选择数据表"
              @change="onDataSourceChange"
              style="width: 100%"
            >
              <el-option
                v-for="source in dataSources"
                :key="source.table_name"
                :label="source.display_name"
                :value="source.table_name"
              >
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%">
                  <span>{{ source.display_name }}</span>
                  <el-tag size="small" type="info">
                    {{ source.row_count }} 条记录
                  </el-tag>
                </div>
              </el-option>
            </el-select>

            <el-button
              v-if="component.dataSource.table"
              type="primary"
              size="small"
              style="width: 100%; margin-top: 8px"
              @click="refreshDataSource"
            >
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </div>

          <!-- 数据筛选 -->
          <div class="property-group" v-if="component.dataSource.table">
            <div class="group-title">
              数据筛选
              <el-button
                size="small"
                text
                @click="addFilter"
              >
                <el-icon><Plus /></el-icon>
                添加条件
              </el-button>
            </div>

            <div
              v-for="(filter, index) in component.dataSource.filters"
              :key="index"
              class="filter-item"
            >
              <el-select
                v-model="filter.field"
                placeholder="字段"
                size="small"
                style="width: 120px"
              >
                <el-option
                  v-for="field in getDataFields(component.dataSource.table)"
                  :key="field.name"
                  :label="field.label || field.name"
                  :value="field.name"
                />
              </el-select>

              <el-select
                v-model="filter.operator"
                size="small"
                style="width: 100px"
              >
                <el-option label="等于" value="eq" />
                <el-option label="包含" value="contains" />
                <el-option label="大于" value="gt" />
                <el-option label="小于" value="lt" />
              </el-select>

              <el-input
                v-model="filter.value"
                placeholder="值"
                size="small"
                style="flex: 1"
              />

              <el-button
                size="small"
                type="danger"
                text
                @click="removeFilter(index)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>

          <!-- 数据排序 -->
          <div class="property-group" v-if="component.dataSource.table">
            <div class="group-title">排序</div>

            <el-select
              v-model="component.dataSource.sortField"
              placeholder="排序字段"
              size="small"
              style="width: 100%"
            >
              <el-option
                v-for="field in getDataFields(component.dataSource.table)"
                :key="field.name"
                :label="field.label || field.name"
                :value="field.name"
              />
            </el-select>

            <el-radio-group
              v-model="component.dataSource.sortOrder"
              size="small"
              style="width: 100%; margin-top: 8px"
            >
              <el-radio-button label="asc">升序</el-radio-button>
              <el-radio-button label="desc">降序</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </el-tab-pane>

      <!-- 样式配置 -->
      <el-tab-pane label="样式" name="style">
        <div class="property-section">
          <!-- 背景颜色 -->
          <div class="property-group">
            <div class="group-title">背景</div>

            <el-form label-position="left" label-width="80px" size="small">
              <el-form-item label="背景色">
                <el-color-picker
                  v-model="component.style.backgroundColor"
                  show-alpha
                  @change="updateStyle('backgroundColor', $event)"
                />
                <el-input
                  v-model="component.style.backgroundColor"
                  placeholder="#FFFFFF"
                  style="width: 120px; margin-left: 8px"
                  @change="updateStyle('backgroundColor', $event)"
                />
              </el-form-item>

              <el-form-item label="边框">
                <el-input
                  v-model="component.style.border"
                  placeholder="1px solid #e0e0e0"
                  @change="updateStyle('border', $event)"
                />
              </el-form-item>

              <el-form-item label="圆角">
                <el-slider
                  v-model="component.style.borderRadius"
                  :min="0"
                  :max="20"
                  @change="updateStyle('borderRadius', $event)"
                />
              </el-form-item>
            </el-form>
          </div>

          <!-- 字体样式 -->
          <div class="property-group">
            <div class="group-title">字体</div>

            <el-form label-position="left" label-width="80px" size="small">
              <el-form-item label="字号">
                <el-select
                  v-model="component.style.fontSize"
                  @change="updateStyle('fontSize', $event)"
                >
                  <el-option label="12px" value="12px" />
                  <el-option label="14px" value="14px" />
                  <el-option label="16px" value="16px" />
                  <el-option label="18px" value="18px" />
                  <el-option label="20px" value="20px" />
                </el-select>
              </el-form-item>

              <el-form-item label="颜色">
                <el-color-picker
                  v-model="component.style.color"
                  @change="updateStyle('color', $event)"
                />
              </el-form-item>

              <el-form-item label="对齐">
                <el-button-group size="small">
                  <el-button
                    :type="component.style.textAlign === 'left' ? 'primary' : ''"
                    @click="updateStyle('textAlign', 'left')"
                  >
                    <el-icon><AlignLeft /></el-icon>
                  </el-button>
                  <el-button
                    :type="component.style.textAlign === 'center' ? 'primary' : ''"
                    @click="updateStyle('textAlign', 'center')"
                  >
                    <el-icon><AlignCenter /></el-icon>
                  </el-button>
                  <el-button
                    :type="component.style.textAlign === 'right' ? 'primary' : ''"
                    @click="updateStyle('textAlign', 'right')"
                  >
                    <el-icon><AlignRight /></el-icon>
                  </el-button>
                </el-button-group>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </el-tab-pane>

      <!-- 交互配置 -->
      <el-tab-pane label="交互" name="interaction">
        <div class="property-section">
          <!-- 点击事件 -->
          <div class="property-group">
            <div class="group-title">
              点击事件
              <el-switch
                v-model="component.interaction.enableClick"
                size="small"
              />
            </div>

            <template v-if="component.interaction.enableClick">
              <el-select
                v-model="component.interaction.onClick.action"
                placeholder="选择动作"
                size="small"
                style="width: 100%"
              >
                <el-option label="打开页面" value="navigate" />
                <el-option label="打开链接" value="link" />
                <el-option label="调用 API" value="api" />
                <el-option label="显示提示" value="message" />
                <el-option label="自定义" value="custom" />
              </el-select>

              <!-- 导航动作配置 -->
              <template v-if="component.interaction.onClick.action === 'navigate'">
                <el-select
                  v-model="component.interaction.onClick.targetPage"
                  placeholder="选择页面"
                  size="small"
                  style="width: 100%; margin-top: 8px"
                >
                  <el-option
                    v-for="page in availablePages"
                    :key="page.id"
                    :label="page.name"
                    :value="page.id"
                  />
                </el-select>
              </template>

              <!-- API 调用配置 -->
              <template v-if="component.interaction.onClick.action === 'api'">
                <el-input
                  v-model="component.interaction.onClick.apiEndpoint"
                  placeholder="/api/..."
                  size="small"
                  style="width: 100%; margin-top: 8px"
                />
              </template>
            </template>
          </div>

          <!-- 权限控制 -->
          <div class="property-group">
            <div class="group-title">权限</div>

            <el-checkbox
              v-model="component.interaction.requireAuth"
              size="small"
            >
              需要登录
            </el-checkbox>

            <el-select
              v-if="component.interaction.requireAuth"
              v-model="component.interaction.allowedRoles"
              multiple
              placeholder="允许的角色"
              size="small"
              style="width: 100%; margin-top: 8px"
            >
              <el-option label="管理员" value="admin" />
              <el-option label="编辑者" value="editor" />
              <el-option label="查看者" value="viewer" />
            </el-select>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import TableProperties from './TableProperties.vue'
import FormProperties from './FormProperties.vue'
import ChartProperties from './ChartProperties.vue'

const props = defineProps({
  component: Object,
  dataSources: Array
})

const emit = defineEmits(['update'])

const activeTab = ref('properties')

function updateProperty(key, value) {
  emit('update', {
    type: 'property',
    key,
    value
  })
}

function updateStyle(key, value) {
  emit('update', {
    type: 'style',
    key,
    value
  })
}

function getDataFields(tableName) {
  const source = props.dataSources.find(s => s.table_name === tableName)
  return source?.schema?.columns || []
}
</script>
```

### 5. 表格组件属性配置

```vue
<template>
  <div class="table-properties">
    <!-- 列配置 -->
    <div class="property-group">
      <div class="group-title">
        列配置
        <el-button
          size="small"
          @click="addColumn"
        >
          <el-icon><Plus /></el-icon>
          添加列
        </el-button>
      </div>

      <draggable
        v-model="localColumns"
        item-key="id"
        handle=".drag-handle"
        @change="onColumnsChange"
      >
        <template #item="{ element: column, index }">
          <div class="column-item">
            <el-icon class="drag-handle" style="cursor: move">
              <DCaret />
            </el-icon>

            <el-input
              v-model="column.field"
              placeholder="字段名"
              size="small"
              style="width: 120px"
              @change="updateColumn(index, 'field', $event)"
            />

            <el-input
              v-model="column.label"
              placeholder="显示名称"
              size="small"
              style="width: 120px"
              @change="updateColumn(index, 'label', $event)"
            />

            <el-select
              v-model="column.type"
              size="small"
              style="width: 100px"
              @change="updateColumn(index, 'type', $event)"
            >
              <el-option label="文本" value="text" />
              <el-option label="数字" value="number" />
              <el-option label="日期" value="date" />
              <el-option label="标签" value="tag" />
              <el-option label="图片" value="image" />
              <el-option label="链接" value="link" />
            </el-select>

            <el-input-number
              v-model="column.width"
              placeholder="宽度"
              size="small"
              :min="50"
              :max="500"
              style="width: 100px"
              @change="updateColumn(index, 'width', $event)"
            />

            <el-switch
              v-model="column.sortable"
              size="small"
              @change="updateColumn(index, 'sortable', $event)"
            />

            <el-button
              size="small"
              type="danger"
              text
              @click="removeColumn(index)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </template>
      </draggable>
    </div>

    <!-- 表格操作 -->
    <div class="property-group">
      <div class="group-title">表格操作</div>

      <el-checkbox-group v-model="localFeatures" @change="onFeaturesChange">
        <el-checkbox label="selectable">可选择</el-checkbox>
        <el-checkbox label="pagination">分页</el-checkbox>
        <el-checkbox label="border">边框</el-checkbox>
        <el-checkbox label="stripe">斑马纹</el-checkbox>
      </el-checkbox-group>
    </div>

    <!-- 操作列 -->
    <div class="property-group">
      <div class="group-title">
        操作列
        <el-switch
          v-model="localActions.enabled"
          size="small"
        />
      </div>

      <template v-if="localActions.enabled">
        <draggable
          v-model="localActions.items"
          item-key="id"
          class="action-list"
        >
          <template #item="{ element: action, index }">
            <div class="action-item">
              <el-select
                v-model="action.type"
                size="small"
                style="width: 100px"
              >
                <el-option label="查看" value="view" />
                <el-option label="编辑" value="edit" />
                <el-option label="删除" value="delete" />
                <el-option label="自定义" value="custom" />
              </el-select>

              <el-input
                v-model="action.label"
                placeholder="按钮文字"
                size="small"
                style="width: 100px"
              />

              <el-select
                v-model="action.buttonType"
                size="small"
                style="width: 100px"
              >
                <el-option label="主要" value="primary" />
                <el-option label="成功" value="success" />
                <el-option label="警告" value="warning" />
                <el-option label="危险" value="danger" />
                <el-option label="文字" value="text" />
              </el-select>

              <el-button
                size="small"
                type="danger"
                text
                @click="removeAction(index)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </template>
        </draggable>

        <el-button
          size="small"
          style="width: 100%; margin-top: 8px"
          @click="addAction"
        >
          <el-icon><Plus /></el-icon>
          添加操作
        </el-button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import draggable from 'vuedraggable'

const props = defineProps({
  component: Object,
  dataSources: Array
})

const emit = defineEmits(['update'])

const localColumns = ref(props.component.props.columns || [])
const localFeatures = ref(props.component.props.features || [])
const localActions = ref(props.component.props.actions || { enabled: false, items: [] })

function addColumn() {
  localColumns.value.push({
    id: `col_${Date.now()}`,
    field: '',
    label: '',
    type: 'text',
    width: 120,
    sortable: true
  })
  emit('update', { key: 'columns', value: localColumns.value })
}

function updateColumn(index, key, value) {
  localColumns.value[index][key] = value
  emit('update', { key: 'columns', value: localColumns.value })
}

function removeColumn(index) {
  localColumns.value.splice(index, 1)
  emit('update', { key: 'columns', value: localColumns.value })
}

function onColumnsChange() {
  emit('update', { key: 'columns', value: localColumns.value })
}
</script>

<style scoped>
.table-properties {
  padding: 16px;
}

.property-group {
  margin-bottom: 24px;
}

.group-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
}

.column-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 8px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 8px;
}
</style>
```

## 快速搭建流程

### 场景 1：3 分钟搭建 CRM 系统

#### 步骤 1：选择模板（30 秒）
```
用户登录 → 点击"新建应用" → 选择"CRM 模板"
```

**模板市场页面**：
```vue
<template>
  <div class="template-market">
    <h2>选择模板开始搭建</h2>

    <div class="template-categories">
      <el-radio-group v-model="selectedCategory" size="large">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="business">业务管理</el-radio-button>
        <el-radio-button label="data">数据管理</el-radio-button>
        <el-radio-button label="automation">自动化</el-radio-button>
      </el-radio-group>
    </div>

    <div class="template-list">
      <!-- CRM 模板卡片 -->
      <div class="template-card" @click="useTemplate('crm')">
        <div class="template-preview">
          <img src="/templates/crm-preview.png" alt="CRM 预览图" />
        </div>
        <div class="template-info">
          <h3>客户关系管理</h3>
          <p>管理客户信息、跟进记录、销售机会</p>
          <div class="template-features">
            <el-tag size="small">客户列表</el-tag>
            <el-tag size="small">跟进记录</el-tag>
            <el-tag size="small">销售漏斗</el-tag>
          </div>
        </div>
        <div class="template-actions">
          <el-button type="primary">使用此模板</el-button>
          <el-button @click.stop="previewTemplate('crm')">预览</el-button>
        </div>
      </div>

      <!-- 其他模板... -->
    </div>
  </div>
</template>
```

#### 步骤 2：连接数据源（30 秒）
```
模板加载 → 系统提示"创建 customers 数据表" → 用户点击"创建表"
→ 可视化表单设计器 → 添加字段（name, email, phone...）
```

**表设计器**：
```vue
<template>
  <div class="table-designer">
    <h3>创建 {{ tableName }} 表</h3>

    <!-- 字段列表 -->
    <el-table :data="columns" style="width: 100%">
      <el-table-column prop="name" label="字段名" width="150">
        <template #default="{ row }">
          <el-input v-model="row.name" placeholder="字段名" size="small" />
        </template>
      </el-table-column>

      <el-table-column prop="type" label="类型" width="150">
        <template #default="{ row }">
          <el-select v-model="row.type" size="small">
            <el-option label="文本" value="string" />
            <el-option label="数字" value="integer" />
            <el-option label="日期" value="datetime" />
            <el-option label="布尔" value="boolean" />
            <el-option label="邮箱" value="email" />
            <el-option label="电话" value="phone" />
          </el-select>
        </template>
      </el-table-column>

      <el-table-column prop="label" label="显示名称" width="150">
        <template #default="{ row }">
          <el-input v-model="row.label" placeholder="显示名称" size="small" />
        </template>
      </el-table-column>

      <el-table-column prop="required" label="必填" width="80">
        <template #default="{ row }">
          <el-switch v-model="row.required" size="small" />
        </template>
      </el-table-column>

      <el-table-column label="操作" width="100">
        <template #default="{ $index }">
          <el-button
            size="small"
            type="danger"
            text
            @click="removeColumn($index)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加字段按钮 -->
    <el-button
      type="primary"
      style="width: 100%; margin-top: 16px"
      @click="addColumn"
    >
      <el-icon><Plus /></el-icon>
      添加字段
    </el-button>

    <!-- 推荐字段 -->
    <div class="suggested-fields" v-if="tableName === 'customers'">
      <h4>推荐字段</h4>
      <el-checkbox-group v-model="selectedFields">
        <el-checkbox label="name">姓名</el-checkbox>
        <el-checkbox label="email">邮箱</el-checkbox>
        <el-checkbox label="phone">电话</el-checkbox>
        <el-checkbox label="company">公司</el-checkbox>
        <el-checkbox label="position">职位</el-checkbox>
        <el-checkbox label="address">地址</el-checkbox>
      </el-checkbox-group>
      <el-button size="small" @click="addSuggestedFields">
        添加推荐字段
      </el-button>
    </div>

    <!-- 创建按钮 -->
    <el-button
      type="primary"
      size="large"
      style="width: 100%; margin-top: 24px"
      @click="createTable"
    >
      创建表
    </el-button>
  </div>
</template>
```

#### 步骤 3：配置页面（1 分钟）
```
表创建完成 → 自动生成"客户列表"页面 → 用户可调整列顺序、显示字段
→ 添加"新建客户"按钮 → 配置表单字段
```

#### 步骤 4：发布应用（30 秒）
```
配置完成 → 点击"发布" → 系统生成应用 URL
→ https://lingnexus.app/apps/crm_abc123
→ 分享给团队成员
```

### 场景 2：从 Excel 导入快速搭建

```
1. 用户上传 Excel 文件
   ↓
2. 系统自动识别表头
   ↓
3. 预览并调整字段类型
   ↓
4. 创建数据表并导入数据
   ↓
5. 自动生成管理页面
   ↓
6. 完成！
```

**导入流程 UI**：

```vue
<template>
  <el-steps :active="currentStep" align-center>
    <el-step title="上传文件" />
    <el-step title="预览数据" />
    <el-step title="调整字段" />
    <el-step title="生成页面" />
    <el-step title="完成" />
  </el-steps>

  <!-- Step 1: 上传 -->
  <div v-if="currentStep === 0" class="step-content">
    <el-upload
      drag
      action="/api/v1/spaces/{spaceId}/import/parse"
      accept=".xlsx,.xls,.csv"
      @success="onFileParsed"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        将文件拖到此处，或<em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 .xlsx, .xls, .csv 格式，最大 10MB
        </div>
      </template>
    </el-upload>
  </div>

  <!-- Step 2: 预览 -->
  <div v-if="currentStep === 1" class="step-content">
    <h3>数据预览</h3>

    <el-table :data="previewData" max-height="400">
      <el-table-column
        v-for="column in columns"
        :key="column.field"
        :prop="column.field"
        :label="column.label"
        :width="120"
      />
    </el-table>

    <div class="step-actions">
      <el-button @click="currentStep--">上一步</el-button>
      <el-button type="primary" @click="currentStep++">
        下一步：调整字段
      </el-button>
    </div>
  </div>

  <!-- Step 3: 调整字段 -->
  <div v-if="currentStep === 2" class="step-content">
    <h3>调整字段配置</h3>

    <el-table :data="columns">
      <el-table-column prop="field" label="字段名" width="150" />
      <el-table-column prop="label" label="显示名称" width="150">
        <template #default="{ row }">
          <el-input v-model="row.label" size="small" />
        </template>
      </el-table-column>
      <el-table-column prop="type" label="数据类型" width="150">
        <template #default="{ row }">
          <el-select v-model="row.type" size="small">
            <el-option label="文本" value="string" />
            <el-option label="数字" value="integer" />
            <el-option label="日期" value="datetime" />
            <el-option label="布尔" value="boolean" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column prop="required" label="必填" width="80">
        <template #default="{ row }">
          <el-switch v-model="row.required" size="small" />
        </template>
      </el-table-column>
    </el-table>

    <div class="step-actions">
      <el-button @click="currentStep--">上一步</el-button>
      <el-button type="primary" @click="createTableAndImport">
        创建表并导入
      </el-button>
    </div>
  </div>

  <!-- Step 4: 生成页面 -->
  <div v-if="currentStep === 3" class="step-content">
    <el-result
      icon="success"
      title="导入成功"
      sub-title="已自动生成管理页面"
    >
      <template #extra>
        <div class="generated-pages">
          <h4>生成的页面</h4>
          <div class="page-list">
            <div class="page-item">
              <el-icon><Grid /></el-icon>
              <span>{{ tableName }} 列表</span>
              <el-tag type="success">已生成</el-tag>
            </div>
            <div class="page-item">
              <el-icon><Plus /></el-icon>
              <span>新建 {{ tableName }}</span>
              <el-tag type="success">已生成</el-tag>
            </div>
          </div>
        </div>

        <div class="step-actions">
          <el-button type="primary" @click="openAppBuilder">
            进入应用构建器
          </el-button>
          <el-button @click="viewApp">
            查看应用
          </el-button>
        </div>
      </template>
    </el-result>
  </div>
</template>
```

## 高级功能

### 1. 实时协作编辑
```typescript
// 使用 WebSocket 实现多人同时编辑
const websocket = new WebSocket(`wss://api.collab/{app_id}`)

websocket.onmessage = (event) => {
  const update = JSON.parse(event.data)

  if (update.type === 'component_update') {
    // 更新组件
    applyRemoteUpdate(update.componentId, update.changes)
  } else if (update.type === 'cursor_position') {
    // 显示协作者光标
    showCollaboratorCursor(update.userId, update.position)
  }
}
```

### 2. 版本历史
```vue
<template>
  <div class="version-history">
    <h3>版本历史</h3>

    <el-timeline>
      <el-timeline-item
        v-for="version in versions"
        :key="version.id"
        :timestamp="formatDate(version.created_at)"
      >
        <el-card>
          <div class="version-header">
            <span>{{ version.message || '自动保存' }}</span>
            <div class="version-actions">
              <el-button size="small" @click="previewVersion(version)">
                预览
              </el-button>
              <el-button size="small" @click="restoreVersion(version)">
                恢复
              </el-button>
            </div>
          </div>
          <div class="version-changes">
            <el-tag
              v-for="change in version.changes"
              :key="change.type"
              size="small"
            >
              {{ getChangeLabel(change) }}
            </el-tag>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>
```

### 3. AI 辅助搭建
```typescript
// AI 对话式构建
async function buildWithAI(prompt: string) {
  const response = await api.post('/ai/build-app', { prompt })

  // AI 返回应用配置
  const appConfig = response.data.config

  // 自动创建组件
  for (const pageConfig of appConfig.pages) {
    for (const componentConfig of pageConfig.components) {
      addComponent(componentConfig)
    }
  }

  // 询问用户是否满意
  ElMessageBox.confirm(
    '已为你生成应用，查看预览？',
    'AI 搭建完成',
    {
      confirmButtonText: '查看',
      cancelButtonText: '继续调整',
      type: 'success'
    }
  )
}

// 示例对话
// 用户："帮我做一个客户管理系统"
// AI："好的，我为你创建了客户管理系统，包含以下功能：
//      1. 客户列表 - 查看所有客户信息
//      2. 新建客户 - 添加新客户
//      3. 客户详情 - 查看客户详细信息
//      4. 跟进记录 - 记录客户沟通历史
//
//      需要调整吗？"
```

## 移动端适配

```vue
<template>
  <div class="mobile-preview">
    <div class="device-frame">
      <!-- iPhone 框架 -->
      <div class="device-notch"></div>

      <!-- 移动端内容 -->
      <div class="device-screen">
        <!-- 状态栏 -->
        <div class="status-bar">
          <span>9:41</span>
          <div class="status-icons">
            <el-icon><Cell /></el-icon>
            <el-icon><Wifi /></el-icon>
            <el-icon><Battery /></el-icon>
          </div>
        </div>

        <!-- 应用内容 -->
        <div class="app-content">
          <ComponentRenderer
            v-for="component in mobileComponents"
            :key="component.id"
            :type="component.type"
            :props="component.props"
            :mobile="true"
          />
        </div>

        <!-- 底部导航 -->
        <div class="tab-bar">
          <div
            v-for="tab in navigation"
            :key="tab.id"
            class="tab-item"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            <el-icon><component :is="tab.icon" /></el-icon>
            <span>{{ tab.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 设备切换 -->
    <div class="device-selector">
      <el-radio-group v-model="selectedDevice" size="small">
        <el-radio-button label="iphone">iPhone 14</el-radio-button>
        <el-radio-button label="ipad">iPad</el-radio-button>
        <el-radio-button label="android">Android</el-radio-button>
      </el-radio-group>
    </div>
  </div>
</template>

<style scoped>
.device-frame {
  width: 375px;
  height: 812px;
  background: #000;
  border-radius: 40px;
  padding: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  margin: 0 auto;
}

.device-notch {
  width: 150px;
  height: 30px;
  background: #000;
  border-radius: 0 0 20px 20px;
  margin: 0 auto;
}

.device-screen {
  width: 100%;
  height: 100%;
  background: #fff;
  border-radius: 28px;
  overflow: hidden;
}
</style>
```

## 总结

这个前端设计方案的核心优势：

✅ **3-3-3 原则**
- 3 秒找到组件
- 30 秒配置页面
- 3 分钟搭建应用

✅ **拖拽式操作**
- 可视化拖拽组件
- 实时预览效果
- 无需编程知识

✅ **智能辅助**
- AI 对话式搭建
- 自动生成配置
- 智能推荐模板

✅ **模板市场**
- CRM、任务管理、库存等
- 一键启用
- 可自定义调整

✅ **多端支持**
- PC 端编辑器
- 移动端预览
- 响应式布局

需要我开始实现某个具体部分吗？比如：
1. 应用构建器主界面
2. 组件库面板
3. 页面画布编辑器
4. 属性配置面板
5. 模板市场页面
