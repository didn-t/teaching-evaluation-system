# app/core/deps.py
from __future__ import annotations

from typing import Callable, List, Optional, Sequence, Tuple
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import TokenData
from app.database import get_db
from app.crud.user import get_user_permissions, get_roles_code


# 管理员角色：默认绕过权限+角色检查（你可以按实际改）
ADMIN_BYPASS_ROLES: Tuple[str, ...] = ("super_admin", "admin")


def get_current_user(request: Request) -> TokenData:
    token_data: Optional[TokenData] = getattr(request.state, "current_user", None)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token验证失败")

    # 如果 TokenData 里带这些字段，可以快速拦截
    if getattr(token_data, "is_delete", False):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户已被删除")
    if getattr(token_data, "status", 1) != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户已被禁用")

    return token_data


async def _get_cached_permissions(request: Request, db: AsyncSession, current_user: TokenData) -> List[str]:
    cached = getattr(request.state, "user_permissions", None)
    if cached is not None:
        return cached
    perms = await get_user_permissions(db, current_user)
    request.state.user_permissions = perms
    return perms


async def _get_cached_roles(request: Request, db: AsyncSession, current_user: TokenData) -> List[str]:
    cached = getattr(request.state, "user_roles", None)
    if cached is not None:
        return cached
    roles = await get_roles_code(db, current_user)
    request.state.user_roles = roles
    return roles


def require_access(
    *,
    roles_any: Sequence[str] = (),
    roles_all: Sequence[str] = (),
    perms_any: Sequence[str] = (),
    perms_all: Sequence[str] = (),
    admin_bypass_roles: Sequence[str] = ADMIN_BYPASS_ROLES,
) -> Callable:
    """
    统一鉴权：角色 + 权限（默认 AND 语义）

    - roles_any：拥有其中任意一个角色即可（如果传了）
    - roles_all：必须拥有全部角色（如果传了）
    - perms_any：拥有其中任意一个权限即可（如果传了）
    - perms_all：必须拥有全部权限（如果传了）
    - admin_bypass_roles：拥有这些角色之一 => 直接放行（可按需关闭）

    规则：
    1) admin_bypass 先判断（可选）
    2) 角色规则通过 AND 权限规则通过 => 放行
    3) roles/perms 都没传 => 只要登录即可
    """

    async def checker(
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        user_roles = await _get_cached_roles(request, db, current_user)

        # 1) 管理员 bypass（可选）
        if admin_bypass_roles and any(r in user_roles for r in admin_bypass_roles):
            return current_user

        # 2) 角色校验
        if roles_all:
            missing = set(roles_all) - set(user_roles)
            if missing:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"缺少角色: {', '.join(sorted(missing))}")

        if roles_any:
            if not any(r in user_roles for r in roles_any):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"需要以下角色之一: {', '.join(roles_any)}")

        # 3) 权限校验
        user_perms = await _get_cached_permissions(request, db, current_user)

        if perms_all:
            missing = set(perms_all) - set(user_perms)
            if missing:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"缺少权限: {', '.join(sorted(missing))}")

        if perms_any:
            if not any(p in user_perms for p in perms_any):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"需要以下权限之一: {', '.join(perms_any)}")

        return current_user

    return checker
