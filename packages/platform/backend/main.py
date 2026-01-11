"""
LingNexus Platform Backend
FastAPI 应用入口
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import init_db
from api.v1 import auth, skills, agents, monitoring, marketplace


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时初始化数据库
    init_db()
    yield
    # 关闭时的清理工作（如果有）


app = FastAPI(
    title="LingNexus Platform",
    description="Low-code platform for building AI agents",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 根路由 ====================

@app.get("/")
async def root():
    """API 根路径"""
    return {
        "message": "LingNexus Platform API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


# ==================== API 路由 ====================

# API v1 路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(skills.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(monitoring.router, prefix="/api/v1")
app.include_router(marketplace.router, prefix="/api/v1")
