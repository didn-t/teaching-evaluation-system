# app/crud/role.py
from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Role, Permission  # 按你的实际路径改


class CRUDRole(CRUDBase[Role]):
    def get_by_code(self, db: Session, *, role_code: str, include_deleted: bool = False) -> Optional[Role]:
        stmt = select(Role).where(Role.role_code == role_code)
        if not include_deleted:
            stmt = stmt.where(Role.is_delete == False)  # noqa: E712
        return db.execute(stmt).scalars().first()

    def set_permissions(self, db: Session, *, role: Role, permissions: Sequence[Permission]) -> Role:
        role.permissions = list(permissions)
        db.commit()
        db.refresh(role)
        return role

    def add_permission(self, db: Session, *, role: Role, permission: Permission) -> Role:
        if permission not in role.permissions:
            role.permissions.append(permission)
            db.commit()
            db.refresh(role)
        return role

    def remove_permission(self, db: Session, *, role: Role, permission: Permission) -> Role:
        if permission in role.permissions:
            role.permissions.remove(permission)
            db.commit()
            db.refresh(role)
        return role


role_crud = CRUDRole(Role)
