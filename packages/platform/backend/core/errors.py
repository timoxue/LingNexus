"""
统一错误处理 - 自定义异常类
"""
from typing import Optional, Any
from fastapi import HTTPException, status


class LingNexusException(Exception):
    """基础异常类"""

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[dict] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(LingNexusException):
    """认证错误"""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[dict] = None
    ):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details
        )


class AuthorizationError(LingNexusException):
    """授权错误"""

    def __init__(
        self,
        message: str = "Permission denied",
        details: Optional[dict] = None
    ):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN,
            details=details
        )


class NotFoundError(LingNexusException):
    """资源未找到错误"""

    def __init__(
        self,
        resource: str,
        identifier: Optional[str] = None,
        details: Optional[dict] = None
    ):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"

        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class ValidationError(LingNexusException):
    """数据验证错误"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[dict] = None
    ):
        if field:
            message = f"Validation failed for '{field}': {message}"

        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class ConflictError(LingNexusException):
    """资源冲突错误"""

    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[dict] = None
    ):
        super().__init__(
            message=message,
            code="CONFLICT_ERROR",
            status_code=status.HTTP_409_CONFLICT,
            details=details
        )


class RateLimitError(LingNexusException):
    """速率限制错误"""

    def __init__(
        self,
        retry_after: Optional[int] = None,
        details: Optional[dict] = None
    ):
        message = "Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"

        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class SkillNotFoundError(NotFoundError):
    """技能未找到错误"""

    def __init__(self, skill_id: int, details: Optional[dict] = None):
        super().__init__(
            resource="Skill",
            identifier=str(skill_id),
            details=details
        )


class AgentNotFoundError(NotFoundError):
    """Agent未找到错误"""

    def __init__(self, agent_id: int, details: Optional[dict] = None):
        super().__init__(
            resource="Agent",
            identifier=str(agent_id),
            details=details
        )


class UserNotFoundError(NotFoundError):
    """用户未找到错误"""

    def __init__(self, user_id: int, details: Optional[dict] = None):
        super().__init__(
            resource="User",
            identifier=str(user_id),
            details=details
        )


class PermissionDeniedError(AuthorizationError):
    """权限拒绝错误（特定操作）"""

    def __init__(
        self,
        resource: str,
        action: str,
        details: Optional[dict] = None
    ):
        message = f"Permission denied: cannot '{action}' {resource}"
        super().__init__(message=message, details=details)


class InvalidCredentialsError(AuthenticationError):
    """无效凭证错误"""

    def __init__(self, details: Optional[dict] = None):
        super().__init__(
            message="Invalid username or password",
            details=details
        )


class DuplicateResourceError(ConflictError):
    """重复资源错误"""

    def __init__(
        self,
        resource: str,
        field: str,
        value: str,
        details: Optional[dict] = None
    ):
        message = f"{resource} with {field} '{value}' already exists"
        super().__init__(message=message, details=details)


class AgentExecutionError(LingNexusException):
    """Agent 执行错误"""

    def __init__(
        self,
        message: str,
        agent_id: Optional[int] = None,
        details: Optional[dict] = None
    ):
        if agent_id:
            message = f"Agent {agent_id} execution failed: {message}"

        super().__init__(
            message=message,
            code="AGENT_EXECUTION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class DatabaseError(LingNexusException):
    """数据库错误"""

    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[dict] = None
    ):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ExternalServiceError(LingNexusException):
    """外部服务错误"""

    def __init__(
        self,
        service: str,
        message: str,
        details: Optional[dict] = None
    ):
        full_message = f"{service} service error: {message}"
        super().__init__(
            message=full_message,
            code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


# 工厂函数
def create_error_response(
    error: LingNexusException,
    include_details: bool = False
) -> dict:
    """创建标准错误响应

    Args:
        error: 异常对象
        include_details: 是否包含详细信息

    Returns:
        错误响应字典
    """
    response = {
        "success": False,
        "error": {
            "code": error.code,
            "message": error.message
        }
    }

    if include_details and error.details:
        response["error"]["details"] = error.details

    return response
