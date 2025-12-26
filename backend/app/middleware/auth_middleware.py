from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core import DEBUG, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.auth import verify_token


class AuthMiddleware(BaseHTTPMiddleware):
    """
    认证和Token设置中间件，用于验证需要token的请求并自动设置token cookie
    """

    async def dispatch(self, request: Request, call_next):
        # 定义不需要认证的路径
        public_paths = [
            "/",
            "/health",
            "/health/db",
            "/api/v1/teaching-eval/user/login",
            "/api/v1/teaching-eval/user/register",
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
                except HTTPException as e:
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
                    max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    path="/"
                )

        return response
