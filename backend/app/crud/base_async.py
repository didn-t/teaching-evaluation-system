# app/crud/base_async.py
from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Sequence, Type, TypeVar, Union

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class CRUDBaseAsync(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        return await db.get(self.model, id)

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[Sequence[Any]] = None,
        order_by: Optional[Sequence[Any]] = None,
        include_deleted: bool = False,
    ) -> List[ModelType]:
        stmt = select(self.model)

        if filters:
            for f in filters:
                stmt = stmt.where(f)

        if not include_deleted and hasattr(self.model, "is_delete"):
            stmt = stmt.where(getattr(self.model, "is_delete") == False)  # noqa: E712

        if order_by:
            stmt = stmt.order_by(*order_by)

        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def count(
        self,
        db: AsyncSession,
        *,
        filters: Optional[Sequence[Any]] = None,
        include_deleted: bool = False,
    ) -> int:
        stmt = select(func.count()).select_from(self.model)

        if filters:
            for f in filters:
                stmt = stmt.where(f)

        if not include_deleted and hasattr(self.model, "is_delete"):
            stmt = stmt.where(getattr(self.model, "is_delete") == False)  # noqa: E712

        result = await db.execute(stmt)
        return int(result.scalar_one())

    async def create(self, db: AsyncSession, *, obj_in: Union[Dict[str, Any], Any]) -> ModelType:
        data = obj_in if isinstance(obj_in, dict) else obj_in.__dict__
        db_obj = self.model(**data)  # type: ignore[arg-type]
        db.add(db_obj)
        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Create failed: integrity error: {e}") from e
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[Dict[str, Any], Any],
        exclude_none: bool = True,
    ) -> ModelType:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.__dict__
        for k, v in update_data.items():
            if exclude_none and v is None:
                continue
            if hasattr(db_obj, k):
                setattr(db_obj, k, v)

        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Update failed: integrity error: {e}") from e

        await db.refresh(db_obj)
        return db_obj

    async def soft_remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        obj = await self.get(db, id=id)
        if not obj:
            return None

        if hasattr(obj, "is_delete"):
            setattr(obj, "is_delete", True)
            await db.commit()
            await db.refresh(obj)
            return obj

        # 没有 is_delete 就硬删
        await db.delete(obj)
        await db.commit()
        return obj

    async def restore(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        obj = await self.get(db, id=id)
        if not obj:
            return None
        if hasattr(obj, "is_delete"):
            setattr(obj, "is_delete", False)
            await db.commit()
            await db.refresh(obj)
        return obj
