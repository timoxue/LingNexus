"""
文件管理 API

提供文件上传、下载、列表、删除等功能
"""
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import datetime

from core.deps import get_db, get_current_active_user
from db.models import User, UserFile, UserFolder, AgentArtifact, AgentExecution
from models.schemas import (
    UserFileCreate,
    UserFileResponse,
    UserFileUpdate,
    UserFolderCreate,
    UserFolderResponse,
    UserFolderUpdate,
    AgentArtifactResponse,
)
from services.file_service import FileService

router = APIRouter(prefix="/files", tags=["files"])


# ==================== 文件上传 ====================

@router.post("/upload", response_model=UserFileResponse)
async def upload_file(
    file: UploadFile = File(...),
    folder_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    上传文件

    - **file**: 要上传的文件
    - **folder_id**: 目标文件夹 ID（可选）
    - **description**: 文件描述（可选）
    """
    try:
        # 保存文件
        file_info = await FileService.save_upload_file(
            file=file,
            user_id=current_user.id,
            folder_id=folder_id,
        )

        # 创建数据库记录
        user_file = UserFile(
            user_id=current_user.id,
            folder_id=folder_id,
            file_id=file_info["file_id"],
            filename=file.filename,
            file_type=file_info["file_type"],
            file_size=file_info["file_size"],
            mime_type=file_info["mime_type"],
            storage_path=file_info["storage_path"],
            description=description,
        )

        db.add(user_file)
        db.commit()
        db.refresh(user_file)

        # 构建响应
        response_data = UserFileResponse.model_validate(user_file).model_dump()
        response_data["download_url"] = f"/api/v1/files/{user_file.file_id}/download"
        response_data["preview_url"] = f"/api/v1/files/{user_file.file_id}/preview"

        return UserFileResponse(**response_data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


# ==================== 文件列表 ====================

@router.get("", response_model=list[UserFileResponse])
async def list_files(
    folder_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取文件列表

    - **folder_id**: 文件夹 ID（可选，不传则获取所有文件）
    - **skip**: 跳过记录数
    - **limit**: 返回记录数
    - **search**: 搜索关键词（可选）
    """
    query = db.query(UserFile).filter(
        UserFile.user_id == current_user.id,
        UserFile.is_deleted == False
    )

    # 文件夹过滤
    if folder_id is not None:
        query = query.filter(UserFile.folder_id == folder_id)

    # 搜索
    if search:
        query = query.filter(UserFile.filename.contains(search))

    # 分页和排序
    files = query.order_by(UserFile.created_at.desc()).offset(skip).limit(limit).all()

    # 构建响应
    result = []
    for file in files:
        file_data = UserFileResponse.model_validate(file).model_dump()
        file_data["download_url"] = f"/api/v1/files/{file.file_id}/download"
        file_data["preview_url"] = f"/api/v1/files/{file.file_id}/preview"
        result.append(UserFileResponse(**file_data))

    return result


# ==================== 文件下载 ====================

@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    下载文件

    - **file_id**: 文件 ID（格式：f_xxxxx）
    """
    # 查询文件
    user_file = db.query(UserFile).filter(
        UserFile.file_id == file_id,
        UserFile.user_id == current_user.id,
        UserFile.is_deleted == False
    ).first()

    if not user_file:
        raise HTTPException(status_code=404, detail="File not found")

    # 更新访问统计
    user_file.access_count += 1
    user_file.last_accessed_at = datetime.datetime.utcnow()
    db.commit()

    # 获取文件路径
    try:
        file_path = FileService.get_file_path(user_file.storage_path)
        return FileResponse(
            path=str(file_path),
            filename=user_file.filename,
            media_type=user_file.mime_type,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {str(e)}")


# ==================== 文件预览 ====================

@router.get("/{file_id}/preview")
async def preview_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    预览文件（在浏览器中直接打开）

    - **file_id**: 文件 ID（格式：f_xxxxx）
    """
    # 查询文件
    user_file = db.query(UserFile).filter(
        UserFile.file_id == file_id,
        UserFile.user_id == current_user.id,
        UserFile.is_deleted == False
    ).first()

    if not user_file:
        raise HTTPException(status_code=404, detail="File not found")

    # 更新访问统计
    user_file.access_count += 1
    user_file.last_accessed_at = datetime.datetime.utcnow()
    db.commit()

    # 获取文件路径
    try:
        file_path = FileService.get_file_path(user_file.storage_path)

        # 根据文件类型返回不同的响应
        if user_file.file_type in ['png', 'jpg', 'jpeg', 'gif', 'txt', 'md', 'json', 'pdf']:
            return FileResponse(
                path=str(file_path),
                media_type=user_file.mime_type,
            )
        else:
            # 其他文件类型提示下载
            return FileResponse(
                path=str(file_path),
                filename=user_file.filename,
                media_type=user_file.mime_type,
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview file: {str(e)}")


# ==================== 文件删除 ====================

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    删除文件（软删除）

    - **file_id**: 文件 ID（格式：f_xxxxx）
    """
    # 查询文件
    user_file = db.query(UserFile).filter(
        UserFile.file_id == file_id,
        UserFile.user_id == current_user.id,
        UserFile.is_deleted == False
    ).first()

    if not user_file:
        raise HTTPException(status_code=404, detail="File not found")

    # 软删除
    user_file.is_deleted = True
    user_file.deleted_at = datetime.datetime.utcnow()
    db.commit()

    # 删除物理文件（可选，如果需要立即释放空间）
    # FileService.delete_file(user_file.storage_path)

    return {"message": "File deleted successfully"}


# ==================== 文件移动 ====================

@router.put("/{file_id}/move", response_model=UserFileResponse)
async def move_file(
    file_id: str,
    target_folder_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    移动文件到文件夹

    - **file_id**: 文件 ID（格式：f_xxxxx）
    - **target_folder_id**: 目标文件夹 ID，None 表示移动到根目录
    """
    # 查询文件
    user_file = db.query(UserFile).filter(
        UserFile.file_id == file_id,
        UserFile.user_id == current_user.id,
        UserFile.is_deleted == False
    ).first()

    if not user_file:
        raise HTTPException(status_code=404, detail="File not found")

    # 验证目标文件夹
    if target_folder_id is not None:
        folder = db.query(UserFolder).filter(
            UserFolder.id == target_folder_id,
            UserFolder.user_id == current_user.id,
            UserFolder.is_deleted == False
        ).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Target folder not found")

    # 移动文件
    user_file.folder_id = target_folder_id
    db.commit()
    db.refresh(user_file)

    # 构建响应
    response_data = UserFileResponse.model_validate(user_file).model_dump()
    response_data["download_url"] = f"/api/v1/files/{user_file.file_id}/download"
    response_data["preview_url"] = f"/api/v1/files/{user_file.file_id}/preview"

    return UserFileResponse(**response_data)


# ==================== 文件夹管理 ====================

@router.post("/folders", response_model=UserFolderResponse)
async def create_folder(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    parent_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    创建文件夹

    - **name**: 文件夹名称
    - **description**: 文件夹描述（可选）
    - **parent_id**: 父文件夹 ID（可选）
    """
    # 计算路径
    path = f"/{name}"
    if parent_id is not None:
        parent_folder = db.query(UserFolder).filter(
            UserFolder.id == parent_id,
            UserFolder.user_id == current_user.id,
            UserFolder.is_deleted == False
        ).first()
        if not parent_folder:
            raise HTTPException(status_code=404, detail="Parent folder not found")
        path = f"{parent_folder.path}/{name}"

    # 检查同名文件夹
    existing = db.query(UserFolder).filter(
        UserFolder.user_id == current_user.id,
        UserFolder.parent_id == parent_id,
        UserFolder.name == name,
        UserFolder.is_deleted == False
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Folder with this name already exists")

    # 创建文件夹
    folder = UserFolder(
        user_id=current_user.id,
        parent_id=parent_id,
        name=name,
        description=description,
        path=path,
    )

    db.add(folder)
    db.commit()
    db.refresh(folder)

    return UserFolderResponse.model_validate(folder)


@router.get("/folders", response_model=list[UserFolderResponse])
async def list_folders(
    parent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取文件夹列表

    - **parent_id**: 父文件夹 ID（可选，None 表示获取根文件夹）
    """
    query = db.query(UserFolder).filter(
        UserFolder.user_id == current_user.id,
        UserFolder.is_deleted == False
    )

    if parent_id is not None:
        query = query.filter(UserFolder.parent_id == parent_id)
    else:
        # 根文件夹（parent_id 为 None）
        query = query.filter(UserFolder.parent_id.is_(None))

    folders = query.order_by(UserFolder.order, UserFolder.created_at).all()

    return [UserFolderResponse.model_validate(f) for f in folders]


@router.put("/folders/{folder_id}", response_model=UserFolderResponse)
async def update_folder(
    folder_id: int,
    folder_update: UserFolderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    更新文件夹

    - **folder_id**: 文件夹 ID
    """
    # 查询文件夹
    folder = db.query(UserFolder).filter(
        UserFolder.id == folder_id,
        UserFolder.user_id == current_user.id,
        UserFolder.is_deleted == False
    ).first()

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # 更新字段
    update_data = folder_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(folder, field, value)

    db.commit()
    db.refresh(folder)

    return UserFolderResponse.model_validate(folder)


@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    删除文件夹（软删除）

    - **folder_id**: 文件夹 ID
    """
    # 查询文件夹
    folder = db.query(UserFolder).filter(
        UserFolder.id == folder_id,
        UserFolder.user_id == current_user.id,
        UserFolder.is_deleted == False
    ).first()

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # 检查是否有子文件夹
    child_count = db.query(UserFolder).filter(
        UserFolder.parent_id == folder_id,
        UserFolder.is_deleted == False
    ).count()
    if child_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete folder with {child_count} sub-folders. Please delete them first."
        )

    # 软删除
    folder.is_deleted = True
    folder.deleted_at = datetime.datetime.utcnow()
    db.commit()

    return {"message": "Folder deleted successfully"}


# ==================== Agent Artifacts ====================

@router.get("/artifacts", response_model=list[AgentArtifactResponse])
async def list_artifacts(
    agent_execution_id: Optional[int] = Query(None),
    skill_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取 Agent 生成的文件列表

    - **agent_execution_id**: Agent 执行 ID（可选）
    - **skill_id**: 技能 ID（可选）
    """
    # 通过 AgentExecution 关联查询
    query = db.query(AgentArtifact).join(AgentExecution).filter(
        AgentExecution.created_by == current_user.id,
        AgentArtifact.is_deleted == False
    )

    if agent_execution_id is not None:
        query = query.filter(AgentArtifact.agent_execution_id == agent_execution_id)

    if skill_id is not None:
        query = query.filter(AgentArtifact.skill_id == skill_id)

    artifacts = query.order_by(AgentArtifact.created_at.desc()).offset(skip).limit(limit).all()

    # 构建响应
    result = []
    for artifact in artifacts:
        artifact_data = AgentArtifactResponse.model_validate(artifact).model_dump()
        artifact_data["download_url"] = f"/api/v1/files/artifacts/{artifact.file_id}/download"
        artifact_data["preview_url"] = f"/api/v1/files/artifacts/{artifact.file_id}/preview"
        result.append(AgentArtifactResponse(**artifact_data))

    return result


@router.get("/artifacts/{file_id}/download")
async def download_artifact(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    下载 Agent 生成的文件

    - **file_id**: 文件 ID（格式：f_xxxxx）
    """
    # 查询文件
    artifact = db.query(AgentArtifact).join(AgentExecution).filter(
        AgentArtifact.file_id == file_id,
        AgentExecution.created_by == current_user.id,
        AgentArtifact.is_deleted == False
    ).first()

    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    # 更新访问统计
    artifact.access_count += 1
    artifact.last_accessed_at = datetime.datetime.utcnow()
    db.commit()

    # 获取文件路径
    try:
        file_path = FileService.get_file_path(artifact.storage_path)
        return FileResponse(
            path=str(file_path),
            filename=artifact.filename,
            media_type=artifact.mime_type,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download artifact: {str(e)}")
