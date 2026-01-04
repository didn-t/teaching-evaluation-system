from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core import DEBUG, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.auth import verify_token
from app.database import AsyncSessionLocal
from app.crud.user import get_roles_code, get_user_permissions

class AuthMiddleware(BaseHTTPMiddleware):
    """
    认证和Token设置中间件，用于验证需要token的请求并自动设置token cookie
    """

    async def dispatch(self, request: Request, call_next):
        # 定义不需要认证的路径
        public_paths = [
            "/",
            "/health",
            "/api/v1/teaching-eval/user/login",
            "/api/v1/teaching-eval/user/register",
            "/api/v1/teaching-eval/system/bootstrap",
            "/api/v1/teaching-eval/system/bootstrap/",
            "/api/v1/teaching-eval/system/db-info",
            "/api/v1/teaching-eval/system/db-info/",
            
        ]

        # 检查是否为公共路径
        if request.url.path in public_paths:
            response = await call_next(request)
        else:
            # 非公共路径，需要验证token
            if (request.url.path.startswith('/static') or
                    request.url.path.startswith('/docs') or
                    request.url.path.startswith('/redoc') or
                    request.url.path.startswith('/openapi')):
                response = await call_next(request)
            else:
                try:
                    token_data = verify_token(request)
                    request.state.current_user = token_data
                    
                    # 获取数据库会话并获取用户角色和权限信息
                    async with AsyncSessionLocal() as db:
                        user_roles = await get_roles_code(db, token_data)
                        user_permissions = await get_user_permissions(db, token_data)
                        
                        # 缓存用户角色和权限信息
                        request.state.user_roles = user_roles
                        request.state.user_permissions = user_permissions
                        
                except HTTPException as e:
                    # 检查是否是来自Authorization头部的token验证失败
                    authorization = request.headers.get("Authorization")
                    if authorization and authorization.startswith("Bearer "):
                        # 如果是Authorization头部的token验证失败，返回标准的401响应
                        return JSONResponse(
                            status_code=e.status_code,
                            content={
                                "code": e.status_code,
                                "msg": e.detail,
                                "data": None
                            }
                        )
                    else:
                        # 其他情况返回标准的401响应
                        return JSONResponse(
                            status_code=e.status_code,
                            content={
                                "code": e.status_code,
                                "msg": e.detail,
                                "data": None
                            }
                        )

                response = await call_next(request)

        # 检查是否需要自动设置token cookie
        token_paths = [
            "/api/v1/teaching-eval/user/login",
            "/api/v1/teaching-eval/user/register",
            "/api/v1/teaching-eval/user/update",
            "/api/v1/teaching-eval/eval/evaluation/submit",
        ]

        if request.url.path in token_paths and request.method in ["POST", "PATCH"]:
            if hasattr(request.state, 'token_to_set') and request.state.token_to_set:
                token_data = request.state.token_to_set
                token_value = token_data if isinstance(token_data, str) else token_data.get('token', token_data)

                response.set_cookie(
                    key="token",
                    value=token_value,
                    httponly=DEBUG,
                    secure=not DEBUG,
                    max_age=int(ACCESS_TOKEN_EXPIRE_MINUTES) * 60,
                    path="/"
                )
                
                # 同时在响应头中设置 Authorization，方便客户端使用
                response.headers["Authorization"] = f"Bearer {token_value}"

        return response