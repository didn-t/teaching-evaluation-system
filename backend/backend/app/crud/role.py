# app/crud/role.py
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_async import CRUDBaseAsync
from app.models import Role, Permission  # 按你的实际路径改


class CRUDRole(CRUDBaseAsync[Role]):
    async def get_by_code(self, db: AsyncSession, *, role_code: str, include_deleted: bool = False) -> Optional[Role]:
        stmt = select(Role).where(Role.role_code == role_code)
        if not include_deleted:
            stmt = stmt.where(Role.is_delete == False)  # noqa: E712
        result = await db.execute(stmt)
        return result.scalars().first()

    async def set_permissions(self, db: AsyncSession, *, role: Role, permissions: Sequence[Permission]) -> Role:
        role.permissions = list(permissions)
        await db.commit()
        await db.refresh(role)
        return role

    async def add_permission(self, db: AsyncSession, *, role: Role, permission: Permission) -> Role:
        if permission not in role.permissions:
            role.permissions.append(permission)
            await db.commit()
            await db.refresh(role)
        return role

    async def remove_permission(self, db: AsyncSession, *, role: Role, permission: Permission) -> Role:
        if permission in role.permissions:
            role.permissions.remove(permission)
            await db.commit()
            await db.refresh(role)
        return role


role_crud = CRUDRole(Role)
