# app/core/deps.py - 依赖注入函数
from fastapi import Request, HTTPException, status
from app.schemas import TokenData


def get_current_user(request: Request) -> TokenData:
    """
    依赖函数：从 request.state 获取当前用户
    中间件已验证 token，这里只需获取数据，验证失败直接抛异常
    """
    token_data = getattr(request.state, 'current_user', None)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token验证失败"
        )
    return token_data
