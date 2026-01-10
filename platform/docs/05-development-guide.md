# 开发指南

## 开发环境搭建

### 1. 准备工作

**安装必要工具**：

```bash
# 安装 Python 3.10+
# Windows: 从 python.org 下载安装
# Linux:
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv

# 安装 Node.js 18+
# Windows: 从 nodejs.org 下载安装
# Linux:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装 Git
# Windows: 从 git-scm.com 下载安装
# Linux:
sudo apt-get install git

# 安装 uv (Python包管理器)
pip install uv
```

### 2. 克隆项目

```bash
git clone https://github.com/your-org/LingNexus.git
cd LingNexus
git checkout skills_market
```

### 3. 后端开发环境

```bash
cd platform/backend

# 安装依赖
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 安装 pre-commit hooks
pre-commit install

# 初始化数据库
python -m scripts.init_db

# 启动开发服务器
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 前端开发环境

```bash
cd platform/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 在另一个终端启动类型检查
npm run type-check

# 启动代码检查
npm run lint
```

### 5. 配置IDE

**VSCode 推荐插件**：
```json
{
  "recommendations": [
    "vue.volar",
    "vue.vscode-typescript-vue-plugin",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "tamasfe.even-better-toml"
  ]
}
```

**VSCode 设置 (.vscode/settings.json)**：
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/platform/backend/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[vue]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

---

## 开发工作流

### 1. 功能开发流程

```bash
# 1. 创建功能分支
git checkout -b feature/skill-editor

# 2. 开发功能
# ...编写代码...

# 3. 运行测试
cd platform/backend
uv run pytest

cd platform/frontend
npm run test

# 4. 代码检查
cd platform/backend
uv run ruff check .
uv run ruff format .

cd platform/frontend
npm run lint

# 5. 提交代码
git add .
git commit -m "feat: 添加Skill编辑器"

# 6. 推送到远程
git push origin feature/skill-editor

# 7. 创建 Pull Request
# 在GitHub/GitLab上创建PR
```

### 2. Commit 规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型 (type)**：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例**：
```bash
feat(skills): 添加Skill编辑器Markdown预览功能

- 实时预览Markdown渲染
- 支持代码高亮
- 添加快捷键支持

Closes #123
```

---

## 代码规范

### Python 代码规范

**遵循 PEP 8**：

```python
# ✅ 好的示例
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class SkillManager:
    """Skill管理器"""

    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self._cache: Optional[dict] = None

    def get_skill(self, skill_id: str) -> Optional[dict]:
        """获取Skill

        Args:
            skill_id: Skill ID

        Returns:
            Skill字典或None
        """
        if not self._cache:
            self._load_cache()
        return self._cache.get(skill_id)


# ❌ 不好的示例
class skillmanager:  # 类名应该大写
    def __init__(self, storage_path):
        self.p=storage_path  # 变量名应该有意义

    def get(self,id):  # 缺少类型注解
        # 缺少文档字符串
        return self.p.get(id)
```

**使用类型注解**：
```python
from typing import List, Dict, Optional, Union

def search_skills(
    keyword: str,
    category: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, any]]:
    """搜索Skills

    Args:
        keyword: 搜索关键词
        category: 分类筛选
        limit: 返回数量限制

    Returns:
        Skill列表
    """
    pass
```

**使用 Pydantic 进行数据验证**：
```python
from pydantic import BaseModel, Field, validator


class SkillCreate(BaseModel):
    """创建Skill请求模型"""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    visibility: str = Field("private", regex="^(private|team|public)$")

    @validator('tags')
    def validate_tags(cls, v):
        """验证标签"""
        if len(v) > 10:
            raise ValueError("最多10个标签")
        return [tag.lower() for tag in v]
```

### Vue/TypeScript 代码规范

**组件风格**：
```vue
<script setup lang="ts">
// ✅ 使用 Composition API + TypeScript
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { Skill } from '@/types/skill'

interface Props {
  skill: Skill
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update', skill: Skill): void
  (e: 'delete', id: string): void
}>()

const router = useRouter()
const loading = ref(false)

const displayName = computed(() => {
  return props.skill.name || '未命名Skill'
})

onMounted(() => {
  console.log('Component mounted')
})
</script>

<template>
  <div class="skill-card">
    <h3>{{ displayName }}</h3>
  </div>
</template>

<style scoped>
.skill-card {
  padding: 16px;
}
</style>
```

**响应式状态管理**：
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSkillStore = defineStore('skill', () => {
  // State
  const skills = ref<Skill[]>([])
  const loading = ref(false)

  // Getters
  const publicSkills = computed(() =>
    skills.value.filter(s => s.visibility === 'public')
  )

  // Actions
  async function fetchSkills() {
    loading.value = true
    try {
      const response = await apiClient.get('/skills')
      skills.value = response.data.items
    } finally {
      loading.value = false
    }
  }

  return {
    skills,
    loading,
    publicSkills,
    fetchSkills
  }
})
```

---

## 测试

### 后端测试

**单元测试 (pytest)**：

```python
# tests/test_skill_manager.py
import pytest
from lingnexus.backend.services.skill_manager import SkillManager
from lingnexus.backend.models.skill import SkillCreate


@pytest.fixture
def skill_manager(tmp_path):
    """创建测试用的SkillManager"""
    return SkillManager(storage_path=str(tmp_path))


def test_create_skill(skill_manager):
    """测试创建Skill"""
    data = SkillCreate(
        name="测试Skill",
        description="这是一个测试",
        author_id="user_123"
    )

    skill_id = skill_manager.create(data)

    assert skill_id is not None
    assert skill_manager.get(skill_id) is not None


def test_list_skills(skill_manager):
    """测试列出Skills"""
    # 创建测试数据
    skill_manager.create(SkillCreate(
        name="Skill1",
        author_id="user_123"
    ))
    skill_manager.create(SkillCreate(
        name="Skill2",
        author_id="user_123"
    ))

    # 测试查询
    skills = skill_manager.list(author_id="user_123")

    assert len(skills) == 2


@pytest.mark.parametrize("visibility,expected", [
    ("private", 0),
    ("public", 2),
])
def test_visibility_filter(skill_manager, visibility, expected):
    """测试可见性筛选"""
    # 创建测试数据
    skill_manager.create(SkillCreate(
        name="Public Skill",
        visibility="public",
        author_id="user_123"
    ))

    skills = skill_manager.list(visibility=visibility)
    assert len(skills) == expected
```

**集成测试**：

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from lingnexus.backend.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


def test_create_skill(client, auth_token):
    """测试创建Skill API"""
    response = client.post(
        "/api/v1/skills",
        json={
            "name": "测试Skill",
            "description": "API测试"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "id" in data["data"]


def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.get("/api/v1/skills")

    assert response.status_code == 401
```

**运行测试**：

```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_skill_manager.py

# 生成覆盖率报告
uv run pytest --cov=lingnexus --cov-report=html
```

### 前端测试

**组件测试 (Vitest)**：

```typescript
// tests/components/SkillCard.spec.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SkillCard from '@/components/skill/SkillCard.vue'
import type { Skill } from '@/types/skill'

describe('SkillCard', () => {
  const mockSkill: Skill = {
    id: 'sk_123',
    name: '测试Skill',
    description: '这是一个测试',
    author_id: 'user_123',
    visibility: 'public',
    rating: 4.5,
    usage_count: 100,
    tags: ['测试', 'Demo']
  }

  it('renders skill name', () => {
    const wrapper = mount(SkillCard, {
      props: { skill: mockSkill }
    })

    expect(wrapper.text()).toContain('测试Skill')
  })

  it('emits click event', async () => {
    const wrapper = mount(SkillCard, {
      props: { skill: mockSkill }
    })

    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('displays rating correctly', () => {
    const wrapper = mount(SkillCard, {
      props: { skill: mockSkill }
    })

    const rating = wrapper.find('.skill-rating')
    expect(rating.text()).toContain('4.5')
  })
})
```

**运行测试**：

```bash
# 运行所有测试
npm run test

# 运行特定测试
npm run test SkillCard

# 生成覆盖率报告
npm run test:coverage
```

---

## 调试技巧

### 后端调试

**使用 pdb 调试**：

```python
def complex_function(data: dict):
    """复杂函数"""
    import pdb; pdb.set_trace()  # 设置断点

    result = process_data(data)
    return result
```

**使用 VSCode 调试**：

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "cwd": "${workspaceFolder}/platform/backend",
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  ]
}
```

### 前端调试

**使用 Vue DevTools**：

1. 安装 Chrome 扩展：Vue.js devtools
2. 打开开发者工具 → Vue 面板
3. 查看组件树、状态、事件

**使用浏览器调试**：

```typescript
// 在代码中添加 debugger
function handleClick() {
  debugger  // 浏览器会在此处暂停
  console.log('Button clicked')
}
```

---

## 性能优化

### 后端优化

**1. 数据库查询优化**：

```python
# ❌ N+1 查询问题
skills = db.query(Skill).all()
for skill in skills:
    author = db.query(User).get(skill.author_id)  # 每次循环都查询

# ✅ 使用 JOIN 预加载
skills = db.query(Skill).options(
    joinedload(Skill.author)
).all()
```

**2. 使用缓存**：

```python
from functools import lru_cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@lru_cache(maxsize=100)
def get_skill_schema(skill_id: str):
    """缓存Skill schema"""
    return skill_manager.get(skill_id)


@router.get("/skills/{skill_id}")
@cache(expire=60)  # 缓存60秒
async def get_skill(skill_id: str):
    return get_skill_schema(skill_id)
```

### 前端优化

**1. 懒加载组件**：

```typescript
// 路由懒加载
const routes = [
  {
    path: '/skills/:id',
    component: () => import('@/views/Skills/SkillDetail.vue')
  }
]

// 组件懒加载
<script setup lang="ts">
const HeavyComponent = defineAsyncComponent(
  () => import('@/components/HeavyComponent.vue')
)
</script>
```

**2. 虚拟滚动**：

```vue
<template>
  <RecycleScroller
    :items="skills"
    :item-size="100"
    key-field="id"
  >
    <template #default="{ item }">
      <SkillCard :skill="item" />
    </template>
  </RecycleScroller>
</template>
```

---

## 常见问题

### 1. CORS 错误

**问题**：前端请求后端API时出现CORS错误

**解决**：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 数据库锁定

**问题**：SQLite 提示 "database is locked"

**解决**：
```python
# 使用 WAL 模式
conn = sqlite3.connect('skills.db')
conn.execute('PRAGMA journal_mode=WAL')

# 或使用连接池
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'sqlite:///skills.db',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### 3. 热重载不工作

**问题**：修改代码后浏览器没有自动刷新

**解决**：
```bash
# 后端：确认使用了 --reload 参数
uvicorn main:app --reload

# 前端：检查 Vite 配置
export default defineConfig({
  server: {
    watch: {
      usePolling: true  # Windows 上可能需要
    }
  }
})
```

---

## 资源链接

### 官方文档
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Vue 3 文档](https://vuejs.org/)
- [Pinia 文档](https://pinia.vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)

### 学习资源
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Vue 3 Composition API](https://vuejs.org/guide/introduction.html)
- [TypeScript 手册](https://www.typescriptlang.org/docs/)

### 工具
- [Pytest](https://docs.pytest.org/)
- [Ruff](https://docs.astral.sh/ruff/)
- [ESLint](https://eslint.org/)
- [Prettier](https://prettier.io/)

---

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

**代码审查清单**：
- [ ] 代码符合规范
- [ ] 添加了测试
- [ ] 测试全部通过
- [ ] 更新了文档
- [ ] 提交信息清晰

---

## 许可证

MIT License - 详见 LICENSE 文件
