"""
速率限制配置
使用 slowapi 实现请求频率限制
"""
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi import status
import logging

logger = logging.getLogger(__name__)


# 创建速率限制器实例
# 使用客户端IP地址作为唯一标识
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/hour"],  # 默认限制：每小时200次
    storage_uri="memory://",      # 使用内存存储（生产环境建议使用Redis）
    headers_enabled=True,         # 在响应头中包含速率限制信息
)


# 自定义速率限制配置
class RateLimitConfig:
    """速率限制配置类"""

    # 认证相关（更严格）
    AUTH_LOGIN = "5/minute"      # 登录：每分钟5次
    AUTH_REGISTER = "3/hour"     # 注册：每小时3次
    AUTH_RESET_PASSWORD = "3/hour"  # 重置密码：每小时3次

    # 技能操作
    SKILL_CREATE = "10/hour"     # 创建技能：每小时10次
    SKILL_UPDATE = "30/hour"     # 更新技能：每小时30次
    SKILL_DELETE = "20/hour"     # 删除技能：每小时20次

    # Agent操作
    AGENT_CREATE = "10/hour"     # 创建Agent：每小时10次
    AGENT_EXECUTE = "60/hour"    # 执行Agent：每小时60次

    # 市场操作
    MARKETPLACE_TRY = "30/hour"  # 试用技能：每小时30次
    MARKETPLACE_SEARCH = "100/hour"  # 搜索：每小时100次

    # 监控数据
    MONITORING_EXPORT = "5/hour"    # 导出数据：每小时5次
    MONITORING_QUERY = "100/hour"   # 查询：每小时100次

    # 通用API
    API_READ = "1000/hour"      # 读取操作：每小时1000次
    API_WRITE = "200/hour"      # 写入操作：每小时200次


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """速率限制超出时的处理器"""

    logger.warning(
        f"Rate limit exceeded: {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "ip": get_remote_address(request)
        }
    )

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please slow down.",
                "details": {
                    "retry_after": exc.retry_after if hasattr(exc, 'retry_after') else 60
                }
            }
        },
        headers={
            "Retry-After": str(exc.retry_after if hasattr(exc, 'retry_after') else 60)
        }
    )


# 速率限制装饰器快捷方式
def limit_login(func):
    """登录速率限制装饰器"""
    return limiter.limit(RateLimitConfig.AUTH_LOGIN)(func)


def limit_register(func):
    """注册速率限制装饰器"""
    return limiter.limit(RateLimitConfig.AUTH_REGISTER)(func)


def limit_skill_create(func):
    """创建技能速率限制装饰器"""
    return limiter.limit(RateLimitConfig.SKILL_CREATE)(func)


def limit_agent_execute(func):
    """执行Agent速率限制装饰器"""
    return limiter.limit(RateLimitConfig.AGENT_EXECUTE)(func)


def limit_marketplace_try(func):
    """试用技能速率限制装饰器"""
    return limiter.limit(RateLimitConfig.MARKETPLACE_TRY)(func)


# IP白名单（可选）
WHITELIST_IPS = [
    "127.0.0.1",
    "::1",
]

def is_whitelisted(ip: str) -> bool:
    """检查IP是否在白名单中"""
    return ip in WHITELIST_IPS


# 带白名单检查的速率限制器
def custom_key_func(request: Request) -> str:
    """
    自定义key函数，支持IP白名单
    白名单IP不受限制
    """
    ip = get_remote_address(request)
    if is_whitelisted(ip):
        return f"whitelisted:{ip}"  # 白名单IP有独立的限制池
    return ip
