# Framework API 参考

> LingNexus Framework 核心 API 文档

---

## 目录

- [Agent API](#agent-api)
- [Skill API](#skill-api)
- [Storage API](#storage-api)
- [Scheduler API](#scheduler-api)
- [Compliance API](#compliance-api)
- [Security API](#security-api)

---

## Agent API

### create_progressive_agent

创建支持渐进式披露的 Agent（推荐使用）。

**函数签名**:
```python
def create_progressive_agent(
    model_name: str = "qwen-max",
    temperature: float = 0.3,
    skills: Optional[List[str]] = None,
    system_prompt: Optional[str] = None,
    memory_enabled: bool = True,
) -> Agent:
    """创建渐进式披露 Agent

    Args:
        model_name: 模型名称（qwen-max, qwen-plus, qwen-turbo, deepseek-chat）
        temperature: 温度参数（0.0-1.0）
        skills: Skill 名称列表
        system_prompt: 系统提示词
        memory_enabled: 是否启用记忆功能

    Returns:
        Agent 实例

    Example:
        >>> agent = create_progressive_agent(
        ...     model_name="qwen-max",
        ...     skills=["合同审查助手"],
        ... )
        >>> response = agent(Msg(name="user", content="审查这份合同"))
    """
```

**返回值**:
- 类型: `Agent`
- Agent 实例，可调用 `agent(message)` 执行

**使用示例**:
```python
from lingnexus import create_progressive_agent
from agentscope.message import Msg

# 基础用法
agent = create_progressive_agent()
response = agent(Msg(name="user", content="你好"))

# 使用 Skills
agent = create_progressive_agent(
    model_name="qwen-max",
    temperature=0.3,
    skills=["合同审查助手", "风险评估工具"],
)

# 自定义系统提示
agent = create_progressive_agent(
    system_prompt="你是一个专业的医学事务助手。",
    skills=["文献检索"],
)
```

---

### create_docx_agent

创建文档处理 Agent。

**函数签名**:
```python
def create_docx_agent(
    model_type: ModelType = ModelType.QWEN,
) -> Agent:
    """创建文档处理 Agent

    Args:
        model_type: 模型类型

    Returns:
        Agent 实例

    Example:
        >>> agent = create_docx_agent()
        >>> response = agent(Msg(name="file", content="contract.docx"))
    """
```

---

## Skill API

### SkillLoader

Skill 加载器，支持渐进式披露。

**类定义**:
```python
class SkillLoader:
    def __init__(self, skills_base: str = "skills"):
        """初始化 Skill 加载器

        Args:
            skills_base: Skills 基础路径
        """
```

**方法**:

#### register_all_skills

```python
def register_all_skills(self) -> None:
    """扫描并注册所有 Skills

    Example:
        >>> loader = SkillLoader()
        >>> loader.register_all_skills()
    """
```

#### get_skill_metadata

```python
def get_skill_metadata(self, skill_name: str) -> Dict:
    """获取 Skill 元数据（Phase 1 - 轻量级）

    Args:
        skill_name: Skill 名称

    Returns:
        {
            "name": str,
            "description": str,
            "category": str,
            "tags": List[str],
        }

    Example:
        >>> metadata = loader.get_skill_metadata("合同审查助手")
        >>> print(metadata["description"])
    """
```

#### load_skill_instructions

```python
def load_skill_instructions(self, skill_name: str) -> str:
    """加载 Skill 完整内容（Phase 2 - 按需）

    Args:
        skill_name: Skill 名称

    Returns:
        完整的 SKILL.md 内容

    Example:
        >>> instructions = loader.load_skill_instructions("合同审查助手")
        >>> print(instructions)
    """
```

#### get_skill_resource_path

```python
def get_skill_resource_path(self, skill_name: str, resource_path: str) -> Path:
    """获取 Skill 资源文件路径（Phase 3 - 按需）

    Args:
        skill_name: Skill 名称
        resource_path: 资源相对路径

    Returns:
        资源文件的完整路径

    Example:
        >>> path = loader.get_skill_resource_path(
        ...     "合同审查助手",
        ...     "references/模板.docx"
        ... )
        >>> print(path)
        /path/to/skills/合同审查助手/references/模板.docx
    """
```

---

### SkillRegistry

Skill 注册表，管理所有已注册的 Skills。

**类定义**:
```python
class SkillRegistry:
    """Skill 注册表"""
```

**方法**:

#### list_all

```python
def list_all(self) -> List[str]:
    """列出所有已注册的 Skill 名称

    Returns:
        Skill 名称列表

    Example:
        >>> registry = SkillRegistry()
        >>> skills = registry.list_all()
        >>> print(skills)
        ["合同审查助手", "风险评估工具", "文献检索"]
    """
```

#### get_by_category

```python
def get_by_category(self, category: str) -> List[str]:
    """按分类获取 Skills

    Args:
        category: 分类名称

    Returns:
        该分类下的 Skill 名称列表

    Example:
        >>> registry = SkillRegistry()
        >>> legal_skills = registry.get_by_category("法务")
    """
```

#### search

```python
def search(self, keyword: str) -> List[str]:
    """搜索 Skills

    Args:
        keyword: 搜索关键词

    Returns:
        匹配的 Skill 名称列表

    Example:
        >>> registry = SkillRegistry()
        >>> results = registry.search("合同")
    """
```

---

## Storage API

### RawStorage

原始数据存储（文件系统）。

**类定义**:
```python
class RawStorage:
    def __init__(self, base_path: str = "data/raw"):
        """初始化原始数据存储

        Args:
            base_path: 基础路径
        """
```

**方法**:

#### save

```python
def save(
    self,
    source: str,
    data: str,
    url: str,
    project: str,
) -> str:
    """保存原始数据

    Args:
        source: 数据源名称
        data: 原始数据（HTML/JSON）
        url: 数据 URL
        project: 项目名称

    Returns:
        data_id: 数据 ID

    Example:
        >>> raw = RawStorage()
        >>> data_id = raw.save(
        ...     source="ClinicalTrials.gov",
        ...     data="<html>...</html>",
        ...     url="https://...",
        ...     project="司美格鲁肽"
        ... )
    """
```

#### load

```python
def load(self, data_id: str) -> str:
    """加载原始数据

    Args:
        data_id: 数据 ID

    Returns:
        原始数据内容

    Example:
        >>> data = raw.load(data_id)
    """
```

---

### StructuredDB

结构化数据存储（SQLite）。

**类定义**:
```python
class StructuredDB:
    def __init__(self, db_path: str = "data/intelligence.db"):
        """初始化结构化数据库

        Args:
            db_path: 数据库文件路径
        """
```

**方法**:

#### save_trial

```python
def save_trial(
    self,
    raw_data_id: str,
    extracted_data: Dict[str, Any],
    project_name: str,
) -> str:
    """保存临床试验数据

    Args:
        raw_data_id: 原始数据 ID
        extracted_data: 提取的结构化数据
        project_name: 项目名称

    Returns:
        trial_id: 试验记录 ID

    Example:
        >>> db = StructuredDB()
        >>> trial_id = db.save_trial(
        ...     raw_data_id="raw_123",
        ...     extracted_data={
        ...         "nct_id": "NCT06989203",
        ...         "title": "Semaglutide Treatment",
        ...         "phase": "III期",
        ...     },
        ...     project_name="司美格鲁肽"
        ... )
    """
```

#### get_project_trials

```python
def get_project_trials(
    self,
    project_name: str,
    limit: int = 20,
    offset: int = 0,
) -> List[Dict]:
    """获取项目的所有试验数据

    Args:
        project_name: 项目名称
        limit: 返回数量限制
        offset: 偏移量

    Returns:
        试验数据列表

    Example:
        >>> trials = db.get_project_trials("司美格鲁肽", limit=10)
        >>> for trial in trials:
        ...     print(f"{trial['nct_id']}: {trial['title']}")
    """
```

#### get_trial_by_nct_id

```python
def get_trial_by_nct_id(self, nct_id: str) -> Optional[Dict]:
    """根据 NCT ID 获取试验数据

    Args:
        nct_id: NCT 编号

    Returns:
        试验数据，如果不存在返回 None

    Example:
        >>> trial = db.get_trial_by_nct_id("NCT06989203")
        >>> if trial:
        ...     print(trial["title"])
    """
```

#### get_all_projects

```python
def get_all_projects(self) -> List[str]:
    """获取所有项目名称

    Returns:
        项目名称列表

    Example:
        >>> projects = db.get_all_projects()
        >>> print(projects)
        ["司美格鲁肽", "替尔泊肽", "度拉糖肽"]
    """
```

#### close

```python
def close(self) -> None:
    """关闭数据库连接

    Example:
        >>> db.close()
    """
```

---

### VectorDB

向量数据库存储（ChromaDB，可选）。

**类定义**:
```python
class VectorDB:
    def __init__(self, db_path: str = "data/vectordb"):
        """初始化向量数据库

        Args:
            db_path: 数据库路径

        Raises:
            ImportError: 如果 ChromaDB 未安装
        """
```

**方法**:

#### add

```python
def add(
    self,
    data_id: str,
    text: str,
    metadata: Dict[str, Any],
) -> None:
    """添加向量数据

    Args:
        data_id: 数据 ID
        text: 要向量化的文本
        metadata: 元数据

    Example:
        >>> vector = VectorDB()
        >>> vector.add(
        ...     data_id="trial_123",
        ...     text="Semaglutide treatment for diabetes",
        ...     metadata={"nct_id": "NCT06989203", "phase": "III期"}
        ... )
    """
```

#### search

```python
def search(
    self,
    query: str,
    top_k: int = 10,
    filter: Optional[Dict] = None,
) -> List[Dict]:
    """语义搜索

    Args:
        query: 查询文本
        top_k: 返回结果数量
        filter: 元数据过滤条件

    Returns:
        搜索结果列表

    Example:
        >>> results = vector.search(
        ...     query="糖尿病治疗",
        ...     top_k=5,
        ...     filter={"phase": "III期"}
        ... )
    """
```

#### count

```python
def count(self) -> int:
    """获取向量总数

    Returns:
        向量总数

    Example:
        >>> total = vector.count()
        >>> print(f"共有 {total} 条向量数据")
    """
```

---

## Scheduler API

### DailyMonitoringTask

每日监控任务，用于自动化数据采集。

**类定义**:
```python
class DailyMonitoringTask:
    def __init__(self, config_path: Optional[str] = None):
        """初始化监控任务

        Args:
            config_path: 配置文件路径，默认为
                         config/projects_monitoring.yaml
        """
```

**方法**:

#### run

```python
def run(
    self,
    project_names: Optional[List[str]] = None,
) -> Dict[str, Dict]:
    """执行监控任务

    Args:
        project_names: 要监控的项目列表，None 表示监控所有项目

    Returns:
        监控结果字典
        {
            "project_name": {
                "source_name": {
                    "items": List[Dict],
                    "count": int,
                    "message": str
                }
            }
        }

    Example:
        >>> task = DailyMonitoringTask()
        >>> results = task.run(project_names=["司美格鲁肽"])
        >>> print(results)
        {
            "司美格鲁肽": {
                "ClinicalTrials.gov": {
                    "items": [...],
                    "count": 10,
                    "message": "成功采集 10 条数据"
                },
                "CDE": {
                    "items": [...],
                    "count": 15,
                    "message": "成功采集 15 条数据"
                }
            }
        }
    """
```

#### get_status

```python
def get_status(self) -> Dict:
    """获取监控状态

    Returns:
        状态信息字典
        {
            "monitored_projects_count": int,
            "structured_projects": List[str],
            "vector_db_count": int,
            "vector_db_available": bool
        }

    Example:
        >>> status = task.get_status()
        >>> print(f"监控项目数: {status['monitored_projects_count']}")
    """
```

---

## Compliance API

### AuditLogger

审计日志记录器。

**类定义**:
```python
class AuditLogger:
    def __init__(self, storage_backend: str = "database"):
        """初始化审计日志记录器

        Args:
            storage_backend: 存储后端（database/file）
        """
```

**方法**:

#### log

```python
async def log(
    self,
    user_id: str,
    action: AuditAction,
    resource_type: str,
    resource_id: str,
    changes: Dict,
    context: Dict,
) -> AuditRecord:
    """记录审计日志

    Args:
        user_id: 用户 ID
        action: 审计动作（CREATE/READ/UPDATE/DELETE/EXECUTE）
        resource_type: 资源类型（skill/agent/trial_data）
        resource_id: 资源 ID
        changes: 变更内容 {"before": ..., "after": ...}
        context: 上下文信息
            {
                "user_name": str,
                "ip_address": str,
                "user_agent": str,
                "result": str,  # "success" | "failure"
                "reason": str,   # 失败原因
            }

    Returns:
        AuditRecord 实例

    Example:
        >>> audit = AuditLogger()
        >>> await audit.log(
        ...     user_id="user_123",
        ...     action=AuditAction.CREATE,
        ...     resource_type="skill",
        ...     resource_id="skill_abc",
        ...     changes={"before": None, "after": skill_data},
        ...     context={
        ...         "user_name": "张三",
        ...         "ip_address": "192.168.1.1",
        ...         "user_agent": "Mozilla/5.0...",
        ...         "result": "success"
        ...     }
        ... )
    """
```

#### query

```python
async def query(
    self,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[AuditRecord]:
    """查询审计日志

    Args:
        user_id: 筛选用户 ID
        resource_type: 筛选资源类型
        start_date: 起始日期
        end_date: 结束日期

    Returns:
        审计记录列表

    Example:
        >>> records = await audit.query(
        ...     user_id="user_123",
        ...     start_date=datetime(2025, 1, 1),
        ...     end_date=datetime(2025, 1, 31)
        ... )
    """
```

#### export_for_regulatory

```python
async def export_for_regulatory(
    self,
    start_date: datetime,
    end_date: datetime,
    format: str = "csv",
) -> str:
    """导出监管机构要求的格式

    Args:
        start_date: 起始日期
        end_date: 结束日期
        format: 导出格式（csv/json）

    Returns:
        导出文件路径

    Example:
        >>> file_path = await audit.export_for_regulatory(
        ...     start_date=datetime(2025, 1, 1),
        ...     end_date=datetime(2025, 1, 31),
        ...     format="csv"
        ... )
        >>> print(f"已导出到: {file_path}")
    """
```

---

## Security API

### EncryptionService

数据加密服务。

**类定义**:
```python
class EncryptionService:
    def __init__(self, master_key: Optional[bytes] = None):
        """初始化加密服务

        Args:
            master_key: 主密钥（如果为 None，从环境变量读取）

        Raises:
            ValueError: 如果未设置 LINGNEXUS_ENCRYPTION_KEY 环境变量
        """
```

**方法**:

#### encrypt

```python
def encrypt(self, plaintext: str) -> str:
    """加密数据

    Args:
        plaintext: 明文

    Returns:
        密文（Base64 编码）

    Example:
        >>> crypto = EncryptionService()
        >>> encrypted = crypto.encrypt("敏感数据")
        >>> print(encrypted)
        gAAAAABl...
    """
```

#### decrypt

```python
def decrypt(self, ciphertext: str) -> str:
    """解密数据

    Args:
        ciphertext: 密文（Base64 编码）

    Returns:
        明文

    Example:
        >>> decrypted = crypto.decrypt(encrypted)
        >>> print(decrypted)
        敏感数据
    """
```

---

### DataMasker

数据脱敏工具。

**方法（静态方法）**:

#### mask_email

```python
@staticmethod
def mask_email(email: str) -> str:
    """脱敏邮箱

    Args:
        email: 邮箱地址

    Returns:
        脱敏后的邮箱

    Example:
        >>> DataMasker.mask_email("zhangsan@example.com")
        'z********n@example.com'
    """
```

#### mask_phone

```python
@staticmethod
def mask_phone(phone: str) -> str:
    """脱敏手机号

    Args:
        phone: 手机号

    Returns:
        脱敏后的手机号

    Example:
        >>> DataMasker.mask_phone("13800138000")
        '138****8000'
    """
```

#### mask_sensitive_data

```python
@staticmethod
def mask_sensitive_data(data: Dict, fields: List[str]) -> Dict:
    """脱敏敏感字段

    Args:
        data: 原始数据
        fields: 需要脱敏的字段列表

    Returns:
        脱敏后的数据

    Example:
        >>> data = {
        ...     "name": "张三",
        ...     "email": "zhangsan@example.com",
        ...     "phone": "13800138000"
        ... }
        >>> masked = DataMasker.mask_sensitive_data(
        ...     data,
        ...     fields=["email", "phone"]
        ... )
        >>> print(masked)
        {
            "name": "张三",
            "email": "z********n@example.com",
            "phone": "138****8000"
        }
    """
```

---

## 异常类

### LingNexusException

基础异常类。

```python
class LingNexusException(Exception):
    """LingNexus 基础异常"""
    pass
```

### SkillNotFoundException

Skill 未找到异常。

```python
class SkillNotFoundException(LingNexusException):
    """Skill 未找到异常"""
    pass
```

### AgentExecutionException

Agent 执行异常。

```python
class AgentExecutionException(LingNexusException):
    """Agent 执行异常"""
    pass
```

---

## 类型定义

### ModelType

模型类型枚举。

```python
class ModelType(str, Enum):
    """模型类型"""
    QWEN = "qwen"
    DEEPSEEK = "deepseek"
```

### AuditAction

审计动作枚举。

```python
class AuditAction(str, Enum):
    """审计动作"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    EXPORT = "export"
    LOGIN = "login"
    LOGOUT = "logout"
```

---

**相关文档**:
- [快速开始](getting-started.md)
- [高级用法](advanced.md)
