"""
LingNexus Platform Backend
FastAPI 应用入口
"""

from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from db import init_db
from api.v1 import auth, skills, agents, monitoring, marketplace
from core.errors import LingNexusException, create_error_response
from core.rate_limit import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


# 加载环境变量（从项目根目录的 .env 文件）
try:
    from dotenv import load_dotenv
    # 获取项目根目录
    # main.py 在 packages/platform/backend/，需要向上4级到达项目根目录
    project_root = Path(__file__).parent.parent.parent.parent
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        logging.info(f"Loaded environment variables from {env_file}")
    else:
        logging.warning(f".env file not found at {env_file}")
except ImportError:
    logging.warning("python-dotenv not installed, environment variables may not be loaded")


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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

# 应用速率限制器
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 全局异常处理器 ====================

@app.exception_handler(LingNexusException)
async def lingnexus_exception_handler(request: Request, exc: LingNexusException):
    """处理 LingNexus 自定义异常"""
    logger.warning(
        f"{exc.code}: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "details": exc.details
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc, include_details=True)
    )


@app.exception_handler(status.HTTP_401_UNAUTHORIZED)
async def unauthorized_handler(request: Request, exc):
    """处理401未授权异常"""
    logger.warning(f"Unauthorized access: {request.url.path}")

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Authentication required"
            }
        }
    )


@app.exception_handler(status.HTTP_403_FORBIDDEN)
async def forbidden_handler(request: Request, exc):
    """处理403禁止访问异常"""
    logger.warning(f"Forbidden access: {request.url.path}")

    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "success": False,
            "error": {
                "code": "FORBIDDEN",
                "message": "Permission denied"
            }
        }
    )


@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def not_found_handler(request: Request, exc):
    """处理404未找到异常"""
    logger.info(f"Resource not found: {request.url.path}")

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": "The requested resource was not found"
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later."
            }
        }
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
