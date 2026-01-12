# 用户个人空间设计方案

从 Agent 工具平台到个人应用开发平台的演进

## 核心理念

**每个用户拥有一个完整的数字工作空间**：
- 📁 文件管理（文件夹组织）
- 🗄️ 数据库（结构化数据存储）
- 🔌 API 发布（对外提供服务）
- 🚀 应用搭建（可视化构建应用）

## 用户空间架构

```
User Space (user_id: 123)
├── 📁 文件系统
│   ├── 📂 Documents/
│   │   ├── 📄 contract.docx
│   │   └── 📄 report.pdf
│   ├── 📂 Images/
│   └── 📂 Projects/
│
├── 🗄️ 数据库（用户创建的表）
│   ├── 📊 customers（客户表）
│   ├── 📊 orders（订单表）
│   └── 📊 products（产品表）
│
├── 🔌 API 端点（用户发布的接口）
│   ├── GET /api/users/123/data/customers
│   ├── POST /api/users/123/data/orders
│   └── GET /api/users/123/files/search
│
└── 🚀 应用（用户搭建的应用）
    ├── 📱 CRM 系统
    ├── 📱 任务管理
    └── 📱 数据看板
```

## 数据库设计

### 1. user_spaces 表（用户空间）

```python
class UserSpace(Base):
    """用户工作空间"""
    __tablename__ = "user_spaces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True)

    # 空间配置
    space_name: Mapped[str] = mapped_column(String(100), default="我的空间")
    space_slug: Mapped[str] = mapped_column(String(50), unique=True)  # URL 友好的标识
    description: Mapped[Optional[str]] = mapped_column(Text)

    # 配置
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否公开
    allow_api_access: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否允许 API 访问
    api_key: Mapped[Optional[str]] = mapped_column(String(64))  # API 密钥

    # 配额
    storage_quota: Mapped[int] = mapped_column(Integer, default=1024*1024*1024)  # 1GB
    storage_used: Mapped[int] = mapped_column(Integer, default=0)
    database_quota: Mapped[int] = mapped_column(Integer, default=100*1024*1024)  # 100MB
    database_used: Mapped[int] = mapped_column(Integer, default=0)

    # 主题配置
    theme_color: Mapped[str] = mapped_column(String(20), default="#409EFF")
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    user: Mapped["User"] = relationship("User", backref="space")
    folders: Mapped[List["SpaceFolder"]] = relationship("SpaceFolder", backref="space", cascade="all, delete-orphan")
    databases: Mapped[List["UserDatabase"]] = relationship("UserDatabase", backref="space", cascade="all, delete-orphan")
    apis: Mapped[List["UserAPI"]] = relationship("UserAPI", backref="space", cascade="all, delete-orphan")
    applications: Mapped[List["UserApplication"]] = relationship("UserApplication", backref="space", cascade="all, delete-orphan")
```

### 2. space_folders 表（文件夹）

```python
class SpaceFolder(Base):
    """空间文件夹"""
    __tablename__ = "space_folders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    space_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_spaces.id"), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("space_folders.id"))  # 父文件夹

    # 文件夹信息
    folder_name: Mapped[str] = mapped_column(String(100))
    folder_path: Mapped[str] = mapped_column(String(500))  # 完整路径，如 /Documents/Projects
    folder_type: Mapped[str] = mapped_column(String(50), default="custom")  # custom, system, agent_outputs

    # 配置
    icon: Mapped[Optional[str]] = mapped_column(String(50))  # 图标名称
    color: Mapped[Optional[str]] = mapped_column(String(20))  # 颜色
    description: Mapped[Optional[str]] = mapped_column(Text)

    # 统计
    file_count: Mapped[int] = mapped_column(Integer, default=0)
    total_size: Mapped[int] = mapped_column(Integer, default=0)

    # 排序
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # 关系
    parent: Mapped[Optional["SpaceFolder"]] = relationship("SpaceFolder", remote_side=[id], backref="children")
    files: Mapped[List["SpaceFile"]] = relationship("SpaceFile", backref="folder", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_space_parent", "space_id", "parent_id"),
        Index("idx_space_path", "space_id", "folder_path"),
    )
```

### 3. space_files 表（文件）

```python
class SpaceFile(Base):
    """空间文件"""
    __tablename__ = "space_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    space_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_spaces.id"), nullable=False)
    folder_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("space_folders.id"))
    agent_execution_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("agent_executions.id"))  # 哪个执行生成的

    # 文件信息
    file_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)  # f_xxxxx
    filename: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(50))
    file_size: Mapped[int] = mapped_column(Integer)
    mime_type: Mapped[str] = mapped_column(String(100))

    # 存储路径
    storage_path: Mapped[str] = mapped_column(String(500))

    # 元数据
    description: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[list]] = mapped_column(JSON)  # 标签

    # 访问控制
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    public_url: Mapped[Optional[str]] = mapped_column(String(100))  # 公开访问的短链接

    # 统计
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    execution: Mapped[Optional["AgentExecution"]] = relationship("AgentExecution")

    __table_args__ = (
        Index("idx_space_folder", "space_id", "folder_id"),
        Index("idx_space_deleted", "space_id", "is_deleted"),
    )
```

### 4. user_databases 表（用户数据库）

```python
class UserDatabase(Base):
    """用户创建的数据库表"""
    __tablename__ = "user_databases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    space_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_spaces.id"), nullable=False)

    # 表信息
    table_name: Mapped[str] = mapped_column(String(100))  # customers, orders 等
    display_name: Mapped[str] = mapped_column(String(100))  # 显示名称
    description: Mapped[Optional[str]] = mapped_column(Text)

    # 表结构定义（JSON Schema）
    schema: Mapped[dict] = mapped_column(JSON)
    # 示例：
    # {
    #   "columns": [
    #     {"name": "id", "type": "integer", "primary_key": true},
    #     {"name": "name", "type": "string", "required": true},
    #     {"name": "email", "type": "string"},
    #     {"name": "created_at", "type": "datetime"}
    #   ]
    # }

    # 数据存储（实际数据）
    data_storage: Mapped[str] = mapped_column(String(100))  # 存储位置：文件路径或外部数据库

    # 配置
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_api_read: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_api_write: Mapped[bool] = mapped_column(Boolean, default=False)

    # 统计
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    storage_size: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    space: Mapped["UserSpace"] = relationship("UserSpace")
    api_endpoints: Mapped[List["UserAPI"]] = relationship("UserAPI", backref="database", cascade="all, delete-orphan")
```

### 5. user_apis 表（用户 API）

```python
class UserAPI(Base):
    """用户发布的 API 端点"""
    __tablename__ = "user_apis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    space_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_spaces.id"), nullable=False)
    database_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("user_databases.id"))  # 关联的数据库表

    # API 信息
    api_name: Mapped[str] = mapped_column(String(100))
    api_slug: Mapped[str] = mapped_column(String(100))  # URL 中的标识
    description: Mapped[Optional[str]] = mapped_column(Text)

    # API 配置
    http_method: Mapped[str] = mapped_column(String(10))  # GET, POST, PUT, DELETE
    endpoint_path: Mapped[str] = mapped_column(String(200))  # /api/spaces/{slug}/data/{table}

    # 访问控制
    require_auth: Mapped[bool] = mapped_column(Boolean, default=True)
    rate_limit: Mapped[Optional[int]] = mapped_column(Integer)  # 每分钟请求限制

    # 统计
    total_calls: Mapped[int] = mapped_column(Integer, default=0)
    last_called_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # 关系
    space: Mapped["UserSpace"] = relationship("UserSpace")
```

### 6. user_applications 表（用户应用）

```python
class UserApplication(Base):
    """用户搭建的应用"""
    __tablename__ = "user_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    space_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_spaces.id"), nullable=False)

    # 应用信息
    app_name: Mapped[str] = mapped_column(String(100))
    app_slug: Mapped[str] = mapped_column(String(100), unique=True)
    app_type: Mapped[str] = mapped_column(String(50))  # crm, task_manager, dashboard, custom
    description: Mapped[Optional[str]] = mapped_column(Text)
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    color: Mapped[Optional[str]] = mapped_column(String(20))

    # 应用配置（JSON）
    config: Mapped[dict] = mapped_column(JSON)
    # 示例：
    # {
    #   "pages": [
    #     {
    #       "name": "客户列表",
    #       "type": "table",
    #       "data_source": "customers",
    #       "columns": ["name", "email", "phone"]
    #     },
    #     {
    #       "name": "客户详情",
    #       "type": "form",
    #       "data_source": "customers",
    #       "fields": [...]
    #     }
    #   ],
    #   "navigation": [...],
    #   "permissions": {...}
    # }

    # 访问控制
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    public_url: Mapped[Optional[str]] = mapped_column(String(100))

    # 统计
    view_count: Mapped[int] = mapped_column(Integer, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关系
    space: Mapped["UserSpace"] = relationship("UserSpace")
```

## 核心功能设计

### 1. 文件管理功能

#### 文件夹操作
```python
@router.post("/spaces/{space_id}/folders")
async def create_folder(
    space_id: int,
    folder_name: str,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """创建文件夹"""
    space = db.query(UserSpace).filter(UserSpace.id == space_id).first()
    if space.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")

    # 构建路径
    if parent_id:
        parent = db.query(SpaceFolder).filter(SpaceFolder.id == parent_id).first()
        folder_path = f"{parent.folder_path}/{folder_name}"
    else:
        folder_path = f"/{folder_name}"

    folder = SpaceFolder(
        space_id=space_id,
        parent_id=parent_id,
        folder_name=folder_name,
        folder_path=folder_path
    )
    db.add(folder)
    db.commit()

    return folder


@router.get("/spaces/{space_id}/folders")
async def list_folders(
    space_id: int,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """列出文件夹"""
    folders = db.query(SpaceFolder).filter(
        SpaceFolder.space_id == space_id,
        SpaceFolder.parent_id == parent_id,
        SpaceFolder.is_deleted == False
    ).all()

    return [{
        "id": f.id,
        "name": f.folder_name,
        "path": f.folder_path,
        "file_count": f.file_count,
        "total_size": f.total_size,
        "children_count": len(f.children)
    } for f in folders]


@router.post("/spaces/{space_id}/files/{file_id}/move")
async def move_file(
    space_id: int,
    file_id: str,
    target_folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """移动文件到文件夹"""
    file = db.query(SpaceFile).filter(
        SpaceFile.file_id == file_id,
        SpaceFile.space_id == space_id
    ).first()

    file.folder_id = target_folder_id
    db.commit()

    return {"message": "File moved successfully"}
```

#### 文件上传
```python
@router.post("/spaces/{space_id}/files/upload")
async def upload_file(
    space_id: int,
    folder_id: Optional[int] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """上传文件到用户空间"""
    import uuid

    # 生成文件 ID
    file_id = f"f_{uuid.uuid4().hex[:12]}"
    unique_filename = f"{file_id}_{file.filename}"

    # 保存文件
    space = db.query(UserSpace).filter(UserSpace.id == space_id).first()
    storage_path = f"spaces/{space.space_slug}/files/{unique_filename}"

    full_path = Path("artifacts") / storage_path
    full_path.parent.mkdir(parents=True, exist_ok=True)

    with open(full_path, "wb") as f:
        f.write(await file.read())

    # 创建记录
    space_file = SpaceFile(
        space_id=space_id,
        folder_id=folder_id,
        file_id=file_id,
        filename=file.filename,
        file_type=file.filename.split('.')[-1],
        file_size=full_path.stat().st_size,
        mime_type=file.content_type,
        storage_path=storage_path
    )

    db.add(space_file)

    # 更新空间配额
    space.storage_used += space_file.file_size

    # 更新文件夹统计
    if folder_id:
        folder = db.query(SpaceFolder).filter(SpaceFolder.id == folder_id).first()
        folder.file_count += 1
        folder.total_size += space_file.file_size

    db.commit()

    return {
        "file_id": file_id,
        "filename": file.filename,
        "download_url": f"/api/v1/spaces/{space_id}/files/{file_id}/download"
    }
```

### 2. 用户数据库功能

#### 创建数据表
```python
@router.post("/spaces/{space_id}/databases")
async def create_database(
    space_id: int,
    table_name: str,
    display_name: str,
    schema: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    创建用户数据表

    Request Body:
    {
        "table_name": "customers",
        "display_name": "客户表",
        "schema": {
            "columns": [
                {"name": "id", "type": "integer", "primary_key": true},
                {"name": "name", "type": "string", "required": true},
                {"name": "email", "type": "string"},
                {"name": "phone", "type": "string"},
                {"name": "company", "type": "string"},
                {"name": "created_at", "type": "datetime", "default": "now"}
            ]
        }
    }
    """
    space = db.query(UserSpace).filter(UserSpace.id == space_id).first()
    if space.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")

    # 创建数据表（使用 SQLite）
    from services.user_database import UserDatabaseManager
    db_mgr = UserDatabaseManager(space.space_slug)

    # 在用户的 SQLite 数据库中创建表
    db_mgr.create_table(table_name, schema)

    # 记录到元数据库
    user_db = UserDatabase(
        space_id=space_id,
        table_name=table_name,
        display_name=display_name,
        schema=schema,
        data_storage=f"spaces/{space.space_slug}/database.db"
    )

    db.add(user_db)
    db.commit()

    return user_db
```

#### 数据 CRUD 操作
```python
@router.get("/spaces/{space_id}/data/{table_name}")
async def query_data(
    space_id: int,
    table_name: str,
    skip: int = 0,
    limit: int = 20,
    filters: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """查询数据表"""
    space = db.query(UserSpace).filter(UserSpace.id == space_id).first()
    user_db = db.query(UserDatabase).filter(
        UserDatabase.space_id == space_id,
        UserDatabase.table_name == table_name
    ).first()

    if not user_db or not user_db.allow_api_read:
        raise HTTPException(403, "Read access denied")

    # 查询用户的数据库
    from services.user_database import UserDatabaseManager
    db_mgr = UserDatabaseManager(space.space_slug)

    data = db_mgr.query(table_name, skip=skip, limit=limit, filters=filters)

    return {
        "table": table_name,
        "total": len(data),
        "data": data
    }


@router.post("/spaces/{space_id}/data/{table_name}")
async def insert_data(
    space_id: int,
    table_name: str,
    row_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """插入数据"""
    space = db.query(UserSpace).filter(UserSpace.id == space_id).first()
    user_db = db.query(UserDatabase).filter(
        UserDatabase.space_id == space_id,
        UserDatabase.table_name == table_name
    ).first()

    if not user_db or not user_db.allow_api_write:
        raise HTTPException(403, "Write access denied")

    from services.user_database import UserDatabaseManager
    db_mgr = UserDatabaseManager(space.space_slug)

    row_id = db_mgr.insert(table_name, row_data)

    # 更新统计
    user_db.row_count += 1
    db.commit()

    return {"id": row_id, "message": "Row inserted successfully"}
```

### 3. API 发布功能

#### 自动生成 API
```python
@router.post("/spaces/{space_id}/apis")
async def publish_api(
    space_id: int,
    api_name: str,
    database_id: int,
    http_method: str,
    require_auth: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    发布 API 端点

    自动为用户的数据表生成 RESTful API
    """
    space = db.query(UserSpace).filter(UserSpace.id == space_id).first()
    user_db = db.query(UserDatabase).filter(UserDatabase.id == database_id).first()

    # 生成 API slug
    api_slug = f"{space.space_slug}_{user_db.table_name}"

    # 创建 API 记录
    user_api = UserAPI(
        space_id=space_id,
        database_id=database_id,
        api_name=api_name,
        api_slug=api_slug,
        http_method=http_method,
        endpoint_path=f"/api/spaces/{space.space_slug}/data/{user_db.table_name}",
        require_auth=require_auth
    )

    db.add(user_api)
    db.commit()

    return {
        "api_id": user_api.id,
        "endpoint_url": f"{BASE_URL}{user_api.endpoint_path}",
        "method": http_method,
        "documentation": f"/api/v1/spaces/{space_id}/apis/{user_api.id}/docs",
        "example": {
            "curl": f"curl -X {http_method} {BASE_URL}{user_api.endpoint_path} \\",
            f"  -H 'Authorization: Bearer {space.api_key}'"
        }
    }
```

#### API 文档生成
```python
@router.get("/spaces/{space_id}/apis/{api_id}/docs")
async def get_api_docs(
    space_id: int,
    api_id: int,
    db: Session = Depends(get_db),
):
    """获取 API 文档"""
    user_api = db.query(UserAPI).filter(UserAPI.id == api_id).first()
    user_db = user_api.database

    # 自动生成 OpenAPI 文档
    docs = {
        "openapi": "3.0.0",
        "info": {
            "title": f"{user_api.api_name}",
            "version": "1.0.0",
            "description": user_api.database.description
        },
        "servers": [
            {"url": f"{BASE_URL}/api/spaces/{user_api.space.space_slug}"}
        ],
        "paths": {
            user_api.endpoint_path: {
                user_api.http_method.lower(): {
                    "summary": f"{user_api.http_method} {user_db.table_name}",
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Row"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Row": {
                    "type": "object",
                    "properties": {
                        col["name"]: {"type": col["type"]}
                        for col in user_db.schema["columns"]
                    }
                }
            }
        }
    }

    return docs
```

### 4. 应用搭建功能

#### 可视化应用配置
```python
@router.post("/spaces/{space_id}/applications")
async def create_application(
    space_id: int,
    app_name: str,
    app_type: str,
    config: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    创建应用

    Request Body (CRM 示例):
    {
        "app_name": "客户关系管理",
        "app_type": "crm",
        "config": {
            "pages": [
                {
                    "id": "customer_list",
                    "name": "客户列表",
                    "type": "table",
                    "data_source": "customers",
                    "columns": [
                        {"field": "name", "label": "姓名", "width": 120},
                        {"field": "email", "label": "邮箱", "width": 200},
                        {"field": "phone", "label": "电话", "width": 150},
                        {"field": "company", "label": "公司", "width": 200}
                    ],
                    "actions": [
                        {"type": "view", "label": "查看"},
                        {"type": "edit", "label": "编辑"},
                        {"type": "delete", "label": "删除"}
                    ],
                    "filters": [
                        {"field": "name", "label": "姓名", "operator": "contains"}
                    ]
                },
                {
                    "id": "customer_detail",
                    "name": "客户详情",
                    "type": "form",
                    "data_source": "customers",
                    "fields": [
                        {"field": "name", "label": "姓名", "required": true},
                        {"field": "email", "label": "邮箱", "type": "email"},
                        {"field": "phone", "label": "电话", "type": "tel"},
                        {"field": "company", "label": "公司"},
                        {"field": "address", "label": "地址", "type": "textarea"}
                    ]
                }
            ],
            "navigation": [
                {"id": "customers", "label": "客户管理", "icon": "el-icon-user", "page": "customer_list"},
                {"id": "settings", "label": "设置", "icon": "el-icon-setting", "page": "settings"}
            ]
        }
    }
    """
    app = UserApplication(
        space_id=space_id,
        app_name=app_name,
        app_type=app_type,
        app_slug=f"{app_type}_{uuid.uuid4().hex[:8]}",
        config=config
    )

    db.add(app)
    db.commit()

    return {
        "app_id": app.id,
        "app_url": f"/apps/{app.app_slug}",
        "edit_url": f"/spaces/{space_id}/applications/{app.id}/edit"
    }
```

#### 应用渲染引擎
```python
@router.get("/apps/{app_slug}")
async def render_application(
    app_slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """渲染用户应用（返回前端配置）"""

    app = db.query(UserApplication).filter(UserApplication.app_slug == app_slug).first()

    if not app or not app.is_active:
        raise HTTPException(404, "Application not found")

    # 检查访问权限
    if not app.is_public:
        # 验证用户登录
        ...

    # 返回应用配置（由前端渲染）
    return {
        "app": {
            "id": app.id,
            "name": app.app_name,
            "type": app.app_type,
            "icon": app.icon,
            "color": app.color
        },
        "config": app.config,
        "data_sources": _load_data_sources(app, db)  # 加载数据源
    }


def _load_data_sources(app: UserApplication, db: Session) -> dict:
    """加载应用需要的数据源"""
    data_sources = {}

    for page in app.config.get("pages", []):
        table_name = page.get("data_source")
        if table_name and table_name not in data_sources:
            user_db = db.query(UserDatabase).filter(
                UserDatabase.space_id == app.space_id,
                UserDatabase.table_name == table_name
            ).first()

            if user_db:
                # 查询数据
                from services.user_database import UserDatabaseManager
                db_mgr = UserDatabaseManager(app.space.space_slug)

                data = db_mgr.query(table_name, limit=100)
                data_sources[table_name] = data

    return data_sources
```

## 前端设计

### 1. 我的空间页面

```vue
<template>
  <div class="my-space">
    <!-- 空间头部 -->
    <div class="space-header">
      <div class="space-info">
        <h1>{{ space.space_name }}</h1>
        <p>{{ space.description }}</p>
      </div>

      <div class="space-stats">
        <el-statistic title="文件数" :value="stats.fileCount" />
        <el-statistic title="存储空间" :value="formatBytes(stats.storageUsed)" />
        <el-statistic title="数据库表" :value="stats.databaseCount" />
        <el-statistic title="API 调用" :value="stats.apiCalls" />
      </div>
    </div>

    <!-- 标签页 -->
    <el-tabs v-model="activeTab">
      <!-- 文件管理 -->
      <el-tab-pane label="文件" name="files">
        <SpaceFileManager :space="space" />
      </el-tab-pane>

      <!-- 数据库 -->
      <el-tab-pane label="数据库" name="database">
        <SpaceDatabaseManager :space="space" />
      </el-tab-pane>

      <!-- API -->
      <el-tab-pane label="API" name="api">
        <SpaceAPIManager :space="space" />
      </el-tab-pane>

      <!-- 应用 -->
      <el-tab-pane label="应用" name="applications">
        <SpaceApplicationManager :space="space" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '@/api'

const route = useRoute()
const space = ref(null)
const stats = ref({})

onMounted(async () => {
  const spaceId = route.params.id
  space.value = await api.get(`/spaces/${spaceId}`)
  stats.value = await api.get(`/spaces/${spaceId}/stats`)
})
</script>
```

### 2. 文件管理组件

```vue
<template>
  <div class="file-manager">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button @click="createFolder">
        <el-icon><FolderAdd /></el-icon>
        新建文件夹
      </el-button>

      <el-upload
        :action="`/api/v1/spaces/${space.id}/files/upload`"
        :show-file-list="false"
        :on-success="onUploadSuccess"
      >
        <el-button>
          <el-icon><Upload /></el-icon>
          上传文件
        </el-button>
      </el-upload>

      <el-button @click="createDatabaseFromFiles">
        <el-icon><Database /></el-icon>
        从文件创建数据库
      </el-button>
    </div>

    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/">
      <el-breadcrumb-item
        v-for="folder in breadcrumb"
        :key="folder.id"
        @click="enterFolder(folder)"
      >
        {{ folder.name }}
      </el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 文件列表 -->
    <div class="file-list">
      <!-- 文件夹 -->
      <div
        v-for="folder in folders"
        :key="folder.id"
        class="file-item folder"
        @dblclick="enterFolder(folder)"
        @click="selectItem(folder, 'folder')"
      >
        <el-icon :size="40" color="#409EFF"><Folder /></el-icon>
        <div class="file-name">{{ folder.folder_name }}</div>
        <div class="file-meta">{{ folder.file_count }} 项</div>
      </div>

      <!-- 文件 -->
      <div
        v-for="file in files"
        :key="file.id"
        class="file-item"
        :class="{ selected: selectedFile?.id === file.id }"
        @click="selectItem(file, 'file')"
      >
        <el-icon :size="40" :color="getFileColor(file.file_type)">
          <component :is="getFileIcon(file.file_type)" />
        </el-icon>
        <div class="file-name">{{ file.filename }}</div>
        <div class="file-meta">{{ formatBytes(file.file_size) }}</div>

        <!-- 操作菜单 -->
        <el-dropdown trigger="click" @command="handleFileCommand($event, file)">
          <el-icon class="more-btn"><MoreFilled /></el-icon>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="download">下载</el-dropdown-item>
              <el-dropdown-item command="move">移动到...</el-dropdown-item>
              <el-dropdown-item command="rename">重命名</el-dropdown-item>
              <el-dropdown-item command="addToDB">添加到数据库</el-dropdown-item>
              <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const props = defineProps({
  space: Object
})

const folders = ref([])
const files = ref([])
const currentFolder = ref(null)

onMounted(async () => {
  loadFolderContents()
})

async function loadFolderContents(folderId = null) {
  const result = await api.get(`/spaces/${props.space.id}/folders`, {
    parent_id: folderId
  })
  folders.value = result.folders
  files.value = result.files
  currentFolder.value = folderId
}

function enterFolder(folder) {
  loadFolderContents(folder.id)
}

async function handleFileCommand(command, file) {
  switch (command) {
    case 'download':
      window.open(`/api/v1/spaces/${props.space.id}/files/${file.file_id}/download`)
      break

    case 'addToDB':
      // 显示数据库选择对话框
      ElMessageBox.prompt(
        '选择目标数据库表',
        '添加到数据库',
        {
          inputType: 'select',
          inputOptions: await loadDatabases()
        }
      ).then(async ({ value }) => {
        await api.post(`/spaces/${props.space.id}/data/${value}/import`, {
          file_id: file.file_id
        })
        ElMessage.success('文件已导入数据库')
      })
      break

    case 'delete':
      await ElMessageBox.confirm('确定要删除这个文件吗？', '确认')
      await api.delete(`/spaces/${props.space.id}/files/${file.file_id}`)
      ElMessage.success('文件已删除')
      loadFolderContents(currentFolder.value)
      break
  }
}
</script>
```

### 3. 数据库管理组件

```vue
<template>
  <div class="database-manager">
    <!-- 数据库列表 -->
    <div class="database-list">
      <div class="toolbar">
        <el-button type="primary" @click="createDatabase">
          <el-icon><Plus /></el-icon>
          创建数据表
        </el-button>

        <el-button @click="importFromFiles">
          <el-icon><Upload /></el-icon>
          从文件导入
        </el-button>
      </div>

      <el-table :data="databases" style="width: 100%">
        <el-table-column prop="display_name" label="表名" />
        <el-table-column prop="table_name" label="标识" />
        <el-table-column prop="row_count" label="记录数" width="100" />
        <el-table-column label="存储" width="120">
          <template #default="{ row }">
            {{ formatBytes(row.storage_size) }}
          </template>
        </el-table-column>
        <el-table-column label="API" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.allow_api_read" type="success" size="small">
              {{ row.allow_api_write ? '读写' : '只读' }}
            </el-tag>
            <el-tag v-else type="info" size="small">未发布</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button size="small" @click="viewData(row)">
              查看数据
            </el-button>
            <el-button size="small" @click="publishAPI(row)">
              发布 API
            </el-button>
            <el-button size="small" @click="createApp(row)">
              搭建应用
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="deleteDatabase(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 数据预览对话框 -->
    <el-dialog v-model="dataDialogVisible" title="数据预览" width="80%">
      <el-table :data="currentData" style="width: 100%">
        <el-table-column
          v-for="column in currentColumns"
          :key="column.name"
          :prop="column.name"
          :label="column.label"
          :width="column.width"
        />
      </el-table>

      <template #footer>
        <el-button @click="exportData">导出 CSV</el-button>
        <el-button type="primary" @click="closeDataDialog">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>
```

## 应用场景示例

### 场景 1：搭建 CRM 系统

```
1. 用户创建 "customers" 数据表
   - 字段：name, email, phone, company, address

2. 上传客户数据 Excel 文件
   - 系统自动导入到 customers 表

3. 发布 API
   - GET /api/spaces/johndoe/data/customers
   - POST /api/spaces/johndoe/data/customers

4. 搭建 CRM 应用
   - 配置"客户列表"页面（表格视图）
   - 配置"客户详情"页面（表单视图）
   - 配置导航和权限

5. 访问应用
   - https://lingnexus.app/apps/crm_abc123
   - 查看、添加、编辑客户
```

### 场景 2：AI Agent 集成

```
1. Agent 生成报告（report.docx）

2. 文件自动保存到用户空间
   - /Documents/Reports/report.docx

3. 用户可以：
   - 在文件管理器中查看
   - 添加到"报告"数据库表
   - 发布 API 供外部调用
   - 在 CRM 应用中关联到客户
```

## 技术架构优势

### 1. 数据隔离
每个用户有独立的 SQLite 数据库文件
```
spaces/
├── user_001/
│   └── database.db  # 用户专属数据库
├── user_002/
│   └── database.db  # 用户专属数据库
```

### 2. 水平扩展
- SQLite → PostgreSQL（数据量大时自动迁移）
- 文件存储 → OSS/S3（文件量大时自动迁移）

### 3. 多租户支持
- 每个用户独立空间
- 独立的 API 密钥
- 独立的配额管理

### 4. 安全性
- 数据库级别的隔离
- API 访问控制
- 文件权限管理

## 实施路线图

### Phase 1: 基础空间（1-2 周）
- ✅ user_spaces 表
- ✅ 文件夹和文件管理
- ✅ 文件上传/下载
- ✅ 基础配额管理

### Phase 2: 用户数据库（2-3 周）
- ✅ user_databases 表
- ✅ 创建/删除数据表
- ✅ 数据 CRUD 操作
- ✅ 从文件导入数据

### Phase 3: API 发布（1-2 周）
- ✅ user_apis 表
- ✅ 自动生成 RESTful API
- ✅ API 密钥管理
- ✅ 访问统计和限流

### Phase 4: 应用搭建（3-4 周）
- ✅ user_applications 表
- ✅ 可视化配置界面
- ✅ 应用渲染引擎
- ✅ 模板市场（CRM、任务管理等）

### Phase 5: 高级功能（持续）
- Agent 与数据集成
- 工作流编排
- Webhook 集成
- 数据可视化

## 总结

这个设计方案的优势：

✅ **渐进式实现**：从文件管理开始，逐步扩展到数据库、API、应用
✅ **向后兼容**：不影响现有 Agent 执行功能
✅ **用户价值**：从"工具"升级为"平台"
✅ **商业模式**：配额销售、API 调用计费、应用市场
✅ **可扩展性**：模块化设计，易于添加新功能

用户可以：
1. 📁 管理文件（文件夹组织）
2. 🗄️ 创建数据库（结构化数据）
3. 🔌 发布 API（对外服务）
4. 🚀 搭建应用（可视化构建）
5. 🤖 集成 Agent（AI 驱动）
