# app/crud/permission.py
from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_async import CRUDBaseAsync
from app.models import Permission  # 按你的实际路径改


class CRUDPermission(CRUDBaseAsync[Permission]):
    async def get_by_code(self, db: AsyncSession, *, permission_code: str, include_deleted: bool = False) -> Optional[Permission]:
        stmt = select(Permission).where(Permission.permission_code == permission_code)
        if not include_deleted:
            stmt = stmt.where(Permission.is_delete == False)  # noqa: E712
        result = await db.execute(stmt)
        return result.scalars().first()

    async def list_tree(self, db: AsyncSession, include_deleted: bool = False) -> List[Dict]:
        # 取全量后内存组树（权限一般不大；如果很大再改递归/CTE）
        perms, _ = await self.get_multi(
            db,
            skip=0,
            limit=10_000,
            include_deleted=include_deleted,
            order_by=[Permission.sort_order.asc(), Permission.id.asc()],
        )

        by_parent: Dict[Optional[int], List[Permission]] = {}
        for p in perms:
            by_parent.setdefault(p.parent_id, []).append(p)

        def build(parent_id: Optional[int]) -> List[Dict]:
            nodes: List[Dict] = []
            for p in by_parent.get(parent_id, []):
                nodes.append({
                    "id": p.id,
                    "code": p.permission_code,
                    "name": p.permission_name,
                    "type": p.permission_type,
                    "sort": p.sort_order,
                    "children": build(p.id),
                })
            return nodes

        return build(None)


permission_crud = CRUDPermission(Permission)
