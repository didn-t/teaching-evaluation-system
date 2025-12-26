# app/core/deps.py - 依赖注入函数
from typing import Callable
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import TokenData
from app.database import get_db
from app.crud.teaching_eval.user import get_user_permissions, get_roles_code


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


def require_permissions(*required_perms: str, require_all: bool = True) -> Callable:
    """
    权限验证依赖工厂

    Args:
        required_perms: 需要的权限列表，如 "user:read", "user:create"
        require_all: True=需要全部权限，False=满足任一权限即可

    Usage:
        @router.get("/users", dependencies=[Depends(require_permissions("user:read"))])
        或
        @router.post("/users")
        async def create_user(
            _: None = Depends(require_permissions("user:create")),
            current_user: TokenData = Depends(get_current_user)
        ):
    """

    async def permission_checker(
            request: Request,
            db: AsyncSession = Depends(get_db),
            current_user: TokenData = Depends(get_current_user)
    ):
        user_perms = await get_user_permissions(db, current_user)

        if require_all:
            # 需要全部权限
            missing = set(required_perms) - set(user_perms)
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少权限: {', '.join(missing)}"
                )
        else:
            # 满足任一权限即可
            if not any(perm in user_perms for perm in required_perms):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"需要以下权限之一: {', '.join(required_perms)}"
                )

        return current_user

    return permission_checker


def require_roles(*required_roles: str, require_all: bool = False) -> Callable:
    """
    角色验证依赖工厂

    Args:
        required_roles: 需要的角色列表，如 "admin", "teacher"
        require_all: True=需要全部角色，False=满足任一角色即可（默认）

    Usage:
        @router.get("/admin", dependencies=[Depends(require_roles("admin"))])
        或
        @router.get("/manage")
        async def manage(
            current_user: TokenData = Depends(require_roles("admin", "manager"))
        ):
    """

    async def role_checker(
            request: Request,
            db: AsyncSession = Depends(get_db),
            current_user: TokenData = Depends(get_current_user)
    ):
        user_roles = await get_roles_code(db, current_user)

        if require_all:
            # 需要全部角色
            missing = set(required_roles) - set(user_roles)
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"缺少角色: {', '.join(missing)}"
                )
        else:
            # 满足任一角色即可
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"需要以下角色之一: {', '.join(required_roles)}"
                )

        return current_user

    return role_checker
