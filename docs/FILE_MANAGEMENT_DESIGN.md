# Agent 文件管理设计方案

## 设计目标

**当前需求**：用户执行 Agent 生成文件后，能够方便地访问和下载
**未来考虑**：为 Workflow 的 Skill 组合预留文件传递机制

## 核心设计原则

### 1. 文件作为 Session 的一部分
```
User Session
├── Chat Messages
├── Agent Executions
└── Generated Files (Session Scope)
```

### 2. 文件引用而非路径传递
```python
# ❌ 不推荐：直接传递路径
"file_path": "/artifacts/2025/1/13/123/document.docx"

# ✅ 推荐：传递文件引用
"file_ref": {
    "file_id": "f_abc123",
    "filename": "document.docx",
    "download_url": "/api/v1/files/f_abc123/download",
    "preview_url": "/api/v1/files/f_abc123/preview"
}
```

### 3. Session 级别的文件管理
- 文件属于某个 Agent Execution
- Execution 属于某个 Session
- Session 内的文件可以被后续的 Agent 调用使用

## 数据库设计

### 1. agent_artifacts 表（核心）

```python
class AgentArtifact(Base):
    """Agent 执行生成的文件"""
    __tablename__ = "agent_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 关联
    agent_execution_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agent_executions.id"), nullable=False
    )
    skill_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("skills.id")  # 哪个 skill 生成的
    )

    # 文件基本信息
    file_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True  # 全局唯一 ID: f_xxxxx
    )
    filename: Mapped[str] = mapped_column(String(255))
    original_filename: Mapped[Optional[str]] = mapped_column(String(255))  # 用户指定的文件名

    # 文件元数据
    file_type: Mapped[str] = mapped_column(String(50))  # docx, pdf, xlsx
    file_size: Mapped[int] = mapped_column(Integer)
    mime_type: Mapped[str] = mapped_column(String(100))

    # 存储路径
    storage_path: Mapped[str] = mapped_column(String(500))  # 相对路径

    # 分类和描述
    category: Mapped[str] = mapped_column(
        String(50), default="document"  # document, image, data, other
    )
    description: Mapped[Optional[str]] = mapped_column(Text)

    # 访问统计
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 状态
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # 关系
    execution: Mapped["AgentExecution"] = relationship("AgentExecution", backref="artifacts")
    skill: Mapped[Optional["Skill"]] = relationship("Skill")

    # 索引
    __table_args__ = (
        Index("idx_execution_artifact", "agent_execution_id"),
        Index("idx_file_id", "file_id"),
        Index("idx_session_file", "agent_execution_id", "is_deleted"),
    )
```

### 2. 为 Workflow 预留的字段

```python
# 当前版本不需要，但为未来预留

# 方式 1: 通过 execution 链追溯
# 在 Workflow 中，多个 AgentExecution 会组成一个链
# 可以通过 execution.parent_execution_id 追溯上一个执行

# 方式 2: 添加 session_id（未来扩展）
class AgentExecution(Base):
    # 现有字段...
    session_id: Mapped[Optional[str]] = mapped_column(String(64))  # 会话 ID
    parent_execution_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("agent_executions.id")
    )
```

## 文件存储方案

### 目录结构（Session 基础）

```
backend/artifacts/
├── sessions/                    # 按 session 分组
│   ├── sess_abc123/            # Session ID
│   │   ├── executions/         # 该 session 的所有执行
│   │   │   ├── exec_001/       # Execution 1
│   │   │   │   ├── f_doc001.docx
│   │   │   │   └── f_img001.png
│   │   │   └── exec_002/       # Execution 2
│   │   │       └── f_doc002.docx
│   │   └── shared/             # Session 共享文件（供后续 Agent 使用）
│   │       └── f_template.docx
```

### 为什么按 Session 分组？

1. **当前需求**：用户在一次对话中可能执行多次 Agent，生成的文件都在同一个会话中
2. **未来扩展**：Workflow 就是多个 Skill 的连续执行，天然属于一个 Session
3. **便于清理**：可以按 Session 清理过期文件
4. **便于传递**：Session 内的文件可以被后续的 Agent 调用

## API 设计

### 1. Agent 执行返回文件列表

```python
@router.post("/{agent_id}/execute", response_model=AgentExecuteResponse)
async def execute_agent(...):
    """执行 Agent - 返回文件列表"""

    result = await run_agent(...)

    # 保存 artifacts 记录
    artifacts = save_artifacts(
        execution_id=execution.id,
        files=result.get("generated_files", []),
        db=db
    )

    return AgentExecuteResponse(
        execution_id=execution.id,
        status=execution.status,
        output_message=execution.output_message,
        artifacts=[{  # 新增字段
            "file_id": a.file_id,
            "filename": a.filename,
            "file_type": a.file_type,
            "download_url": f"/api/v1/files/{a.file_id}/download",
            "preview_url": f"/api/v1/files/{a.file_id}/preview" if can_preview(a) else None
        } for a in artifacts]
    )
```

### 2. 文件下载 API

```python
@router.get("/files/{file_id}/download")
async def download_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """下载文件"""

    # 查询文件记录
    artifact = db.query(AgentArtifact).filter(
        AgentArtifact.file_id == file_id,
        AgentArtifact.is_deleted == False
    ).first()

    if not artifact:
        raise HTTPException(404, "File not found")

    # 验证权限（用户只能下载自己 execution 的文件）
    execution = artifact.execution
    agent = execution.agent

    if agent.created_by != current_user.id:
        raise HTTPException(403, "Access denied")

    # 构建文件路径
    from pathlib import Path
    file_path = Path("artifacts") / artifact.storage_path

    if not file_path.exists():
        raise HTTPException(404, "File not found on disk")

    # 更新访问统计
    artifact.access_count += 1
    artifact.last_accessed_at = datetime.utcnow()
    db.commit()

    # 返回文件
    from fastapi.responses import FileResponse
    return FileResponse(
        path=str(file_path),
        filename=artifact.original_filename or artifact.filename,
        media_type=artifact.mime_type
    )
```

### 3. Session 文件列表（为未来 Workflow 预留）

```python
@router.get("/sessions/{session_id}/files")
async def list_session_files(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取 Session 内的所有可用文件

    未来用途：在 Workflow 中，后续 Skill 可以引用前面生成的文件
    """

    # 查询该 session 的所有 execution
    executions = db.query(AgentExecution).filter(
        AgentExecution.session_id == session_id,
        AgentExecution.created_by == current_user.id
    ).all()

    execution_ids = [e.id for e in executions]

    # 查询这些 execution 生成的文件
    artifacts = db.query(AgentArtifact).filter(
        AgentArtifact.agent_execution_id.in_(execution_ids),
        AgentArtifact.is_deleted == False
    ).order_by(AgentArtifact.created_at.desc()).all()

    return [{
        "file_id": a.file_id,
        "filename": a.filename,
        "file_type": a.file_type,
        "created_at": a.created_at,
        "execution_id": a.agent_execution_id,
        "skill_name": a.skill.name if a.skill else "unknown",
        "download_url": f"/api/v1/files/{a.file_id}/download",
        "reference": f"{{{{file:{a.file_id}}}}}"  # 引用语法（未来 Workflow 用）
    } for a in artifacts]
```

### 4. 上传文件（为未来 Workflow 预留）

```python
@router.post("/sessions/{session_id}/upload")
async def upload_file_to_session(
    session_id: str,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    上传文件到 Session

    未来用途：用户可以上传模板文件，供 Workflow 中的 Skill 使用
    """

    # 保存文件
    file_id = generate_file_id()
    storage_path = f"sessions/{session_id}/shared/{file_id}_{file.filename}"

    full_path = Path("artifacts") / storage_path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    with open(full_path, "wb") as f:
        f.write(await file.read())

    # 创建记录
    artifact = AgentArtifact(
        agent_execution_id=None,  # Session 级别的文件
        file_id=file_id,
        filename=file.filename,
        original_filename=file.filename,
        file_type=get_file_type(file.filename),
        file_size=full_path.stat().st_size,
        mime_type=file.content_type,
        storage_path=storage_path,
        category="user_upload"
    )

    db.add(artifact)
    db.commit()

    return {
        "file_id": file_id,
        "filename": file.filename,
        "reference": f"{{{{file:{file_id}}}}}"
    }
```

## Tool 函数改造

### 当前：返回文件引用信息

```python
# skills/external/docx/scripts/tools.py

def create_new_docx(
    filename: str = "document.docx",
    content: str = ""
) -> str:
    """创建 Word 文档"""
    try:
        from docx import Document
        import uuid
        from pathlib import Path

        # 生成唯一文件 ID
        file_id = f"f_{uuid.uuid4().hex[:12]}"
        unique_filename = f"{file_id}_{filename}"

        # 创建文档
        doc = Document()
        if content:
            doc.add_paragraph(content)

        # 保存到 artifacts 目录（相对于当前工作目录）
        artifacts_dir = Path.cwd() / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        output_path = artifacts_dir / unique_filename
        doc.save(str(output_path))

        # 返回文件信息（JSON 格式）
        import json
        result = {
            "file_id": file_id,
            "filename": filename,
            "file_type": "docx",
            "file_size": output_path.stat().st_size,
            "temp_path": str(output_path)  # 临时路径，会被 AgentService 移动
        }

        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
```

### AgentService：捕获并保存文件

```python
# services/agent_service.py

async def execute(self, ...):
    """执行 Agent"""
    import tempfile
    import shutil
    import os
    from pathlib import Path

    # 创建临时工作目录
    temp_workdir = Path(tempfile.mkdtemp(prefix="agent_execution_"))
    old_cwd = os.getcwd()

    generated_files = []  # 记录生成的文件

    try:
        # 切换到临时目录
        os.chdir(temp_workdir)

        # 执行 Agent
        response = await agent(user_msg)

        # 扫描生成的文件
        for file_path in temp_workdir.iterdir():
            if file_path.is_file() and file_path.suffix in ['.docx', '.pdf', '.xlsx', '.png', '.jpg']:
                generated_files.append(file_path)

    finally:
        os.chdir(old_cwd)

    # 处理生成的文件
    artifacts = []
    for file_path in generated_files:
        # 读取文件信息（从 tool 返回值中）
        file_info = self._extract_file_info(response, file_path)

        if file_info:
            # 移动到正式存储位置
            session_id = self._get_session_id(execution_id, db)
            storage_path = f"sessions/{session_id}/executions/{execution_id}/{file_path.name}"

            artifacts_dir = Path("artifacts")
            target_path = artifacts_dir / storage_path
            target_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.move(str(file_path), str(target_path))

            # 保存到数据库
            artifact = AgentArtifact(
                agent_execution_id=execution_id,
                file_id=file_info['file_id'],
                filename=file_path.name,
                original_filename=file_info.get('filename'),
                file_type=file_info['file_type'],
                file_size=file_info['file_size'],
                mime_type=file_info.get('mime_type', 'application/octet-stream'),
                storage_path=storage_path,
                description=f"Generated by {file_info.get('skill', 'agent')}"
            )

            db.add(artifact)
            artifacts.append(artifact)

    db.commit()

    # 清理临时目录
    shutil.rmtree(temp_workdir, ignore_errors=True)

    return {
        "status": "success",
        "output_message": output_message,
        "artifacts": [a.to_dict() for a in artifacts]
    }

def _extract_file_info(self, response, file_path) -> Optional[Dict]:
    """从响应中提取文件信息"""
    # 解析 tool 返回的 JSON
    # 这里需要从 response.content 中提取 tool 调用结果
    # 简化实现：从文件名解析 file_id
    filename = file_path.name
    if '_' in filename:
        file_id = filename.split('_')[0]
        return {
            'file_id': file_id,
            'file_type': file_path.suffix.lstrip('.'),
            'file_size': file_path.stat().st_size
        }
    return None
```

## 前端设计

### 1. 执行结果展示（当前可用）

```vue
<template>
  <div class="execution-result">
    <!-- 输出消息 -->
    <div class="output-message">
      {{ execution.output_message }}
    </div>

    <!-- 生成的文件 -->
    <div v-if="execution.artifacts && execution.artifacts.length > 0" class="artifacts">
      <h4>生成的文件 ({{ execution.artifacts.length }})</h4>

      <div class="file-list">
        <div
          v-for="artifact in execution.artifacts"
          :key="artifact.file_id"
          class="file-item"
        >
          <!-- 文件图标 -->
          <el-icon :class="getFileIcon(artifact.file_type)" size="32" />

          <!-- 文件信息 -->
          <div class="file-info">
            <div class="filename">{{ artifact.filename }}</div>
            <div class="meta">
              {{ formatFileSize(artifact.file_size || 0) }} •
              {{ artifact.file_type.toUpperCase() }}
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="actions">
            <!-- 下载 -->
            <el-button
              type="primary"
              size="small"
              @click="downloadFile(artifact.file_id)"
            >
              下载
            </el-button>

            <!-- 预览（如果支持） -->
            <el-button
              v-if="canPreview(artifact.file_type)"
              size="small"
              @click="previewFile(artifact)"
            >
              预览
            </el-button>

            <!-- 用于后续 Agent（未来扩展） -->
            <el-dropdown @command="useFile($event, artifact)">
              <el-button size="small">
                用于<el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="next_agent">
                    发送给后续 Agent
                  </el-dropdown-item>
                  <el-dropdown-item command="upload_to_session">
                    保存到会话（供后续使用）
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  execution: {
    type: Object,
    required: true
  }
})

// 下载文件
async function downloadFile(fileId) {
  try {
    const url = `/api/v1/files/${fileId}/download`
    window.open(url, '_blank')
    ElMessage.success('下载开始')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 预览文件
async function previewFile(artifact) {
  // 显示预览对话框
  previewDialogVisible.value = true
  currentPreviewFile.value = artifact

  // 加载预览内容
  if (artifact.preview_url) {
    const response = await api.get(artifact.preview_url)
    previewContent.value = response.data
  }
}

// 未来扩展：用于后续 Agent
function useFile(command, artifact) {
  if (command === 'next_agent') {
    // 打开新的 Agent 执行对话框，自动附加文件引用
    ElMessageBox.prompt(
      '请输入新 Agent 的执行消息',
      '发送给后续 Agent',
      {
        inputValue: `请处理这个文件：{{file:${artifact.file_id}}}`
      }
    ).then(({ value }) => {
      executeAgent(agentId, value, [artifact.file_id])
    })
  } else if (command === 'upload_to_session') {
    // 将文件上传到 Session 共享目录
    ElMessage.success('文件已保存到会话，可供后续 Agent 使用')
  }
}

// 判断是否可以预览
function canPreview(fileType) {
  return ['txt', 'md', 'json', 'png', 'jpg', 'jpeg', 'gif'].includes(fileType)
}

// 获取文件图标
function getFileIcon(fileType) {
  const icons = {
    'docx': 'el-icon-document',
    'pdf': 'el-icon-document',
    'xlsx': 'el-icon-s-grid',
    'png': 'el-icon-picture',
    'jpg': 'el-icon-picture',
    'txt': 'el-icon-tickets',
  }
  return icons[fileType] || 'el-icon-document'
}
</script>
```

### 2. 我的文件页面（当前可用）

```vue
<template>
  <div class="my-files">
    <h2>我的文件</h2>

    <!-- 过滤器 -->
    <div class="filters">
      <el-select v-model="filterType" placeholder="文件类型" clearable>
        <el-option label="全部" value=""></el-option>
        <el-option label="Word 文档" value="docx"></el-option>
        <el-option label="PDF" value="pdf"></el-option>
        <el-option label="Excel" value="xlsx"></el-option>
      </el-select>

      <el-select v-model="filterSource" placeholder="来源" clearable>
        <el-option label="全部" value=""></el-option>
        <el-option label="Agent 生成" value="agent"></el-option>
        <el-option label="用户上传" value="user_upload"></el-option>
      </el-select>
    </div>

    <!-- 文件列表 -->
    <el-table :data="filteredFiles" style="width: 100%">
      <el-table-column prop="filename" label="文件名" />
      <el-table-column prop="file_type" label="类型" width="100" />
      <el-table-column label="大小" width="120">
        <template #default="{ row }">
          {{ formatFileSize(row.file_size) }}
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250">
        <template #default="{ row }">
          <el-button size="small" @click="download(row)">下载</el-button>
          <el-button
            v-if="canPreview(row.file_type)"
            size="small"
            @click="preview(row)"
          >
            预览
          </el-button>
          <el-button
            size="small"
            type="success"
            @click="useInAgent(row)"
          >
            用于 Agent
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
```

## 为未来 Workflow 预留的设计

### 1. 文件引用语法

```
# 当前版本：在 UI 中选择文件
用户点击"用于 Agent"按钮 -> 选择文件

# 未来版本：支持引用语法
用户输入：请处理上一个 Agent 生成的文件：{{file:f_abc123}}

系统自动解析：
1. 识别 {{file:xxx}} 语法
2. 从 Session 文件列表中查找 f_abc123
3. 将文件传递给 Agent
4. Agent 可以通过 Tool 访问文件
```

### 2. Skill 的输入参数定义（未来扩展）

```yaml
# skills/external/docx/SKILL.md

---
name: docx
description: "Word 文档处理"

inputs:
  - name: template_file
    type: file
    description: "模板文件"
    file_types: [docx, doc]
    required: false

  - name: content
    type: string
    description: "文档内容"
    required: true

outputs:
  - name: document
    type: file
    description: "生成的文档"
---
```

未来在 Workflow 中：
```json
{
  "node_1": {
    "skill": "docx",
    "inputs": {
      "content": "Hello World"
    },
    "outputs": {
      "document": "{{file:f_out1}}"  // 输出文件
    }
  },
  "node_2": {
    "skill": "pdf_converter",
    "inputs": {
      "source_file": "{{file:f_out1}}"  // 引用 node_1 的输出
    }
  }
}
```

## 实施步骤

### Phase 1: 核心功能（当前实现）

1. ✅ 创建 `agent_artifacts` 表
2. ✅ 改造 Tool 函数返回文件信息
3. ✅ AgentService 捕获并保存文件
4. ✅ 提供文件下载 API
5. ✅ 前端显示生成的文件

### Phase 2: 用户体验优化

1. 添加文件预览功能（文本、图片）
2. "我的文件"页面
3. 文件重新命名
4. 批量下载（打包成 zip）

### Phase 3: 为 Workflow 预留（不立即实现）

1. 添加 `session_id` 字段
2. 提供 Session 文件列表 API
3. 文件引用语法设计（`{{file:xxx}}`）
4. 文件上传到 Session API

### Phase 4: Workflow 集成（未来）

1. Skill 输入输出定义
2. 文件引用解析器
3. Workflow 编排器
4. 可视化 Workflow 编辑器

## 总结

这个设计方案的核心优势：

### ✅ 当前可用
- 立即解决用户访问生成文件的问题
- 提供下载、预览功能
- 清晰的文件管理

### ✅ 向前兼容
- 文件有唯一 ID（`file_id`）
- 支持引用语法（`{{file:xxx}}`）
- Session 级别的文件管理
- 为 Workflow 预留接口

### ✅ 用户体验
- 直观的文件列表
- 一键下载
- 方便的文件传递（未来）
