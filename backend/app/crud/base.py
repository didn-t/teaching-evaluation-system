# app/crud/base.py
from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Sequence, Type, TypeVar, Union

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
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
    ) -> tuple[List[ModelType], int]:
        # 构建查询语句
        stmt = select(self.model)

        # 添加过滤条件
        if filters:
            for f in filters:
                stmt = stmt.where(f)

        # 默认排除软删除
        if not include_deleted and hasattr(self.model, "is_delete"):
            stmt = stmt.where(getattr(self.model, "is_delete") == False)  # noqa: E712

        # 添加排序
        if order_by:
            stmt = stmt.order_by(*order_by)

        # 添加分页
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        items = list(result.scalars().all())

        # 计算总数
        count_stmt = select(func.count()).select_from(self.model)
        if filters:
            for f in filters:
                count_stmt = count_stmt.where(f)
        if not include_deleted and hasattr(self.model, "is_delete"):
            count_stmt = count_stmt.where(getattr(self.model, "is_delete") == False)  # noqa: E712
        count_result = await db.execute(count_stmt)
        total = count_result.scalar_one()

        return items, total

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
        if isinstance(obj_in, dict):
            data = obj_in
        else:
            # 使用model_dump()替代__dict__，避免pydantic v2的兼容性问题
            data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in.dict()
        
        db_obj = self.model(**data)  # type: ignore[arg-type]
        db.add(db_obj)
        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Create failed due to integrity error: {e}") from e

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[Dict[str, Any], Any],
        exclude_unset: bool = True,
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # 使用model_dump()替代__dict__，避免pydantic v2的兼容性问题
            update_data = obj_in.model_dump(exclude_unset=exclude_unset) if hasattr(obj_in, "model_dump") else obj_in.dict(exclude_unset=exclude_unset)

        for field, value in update_data.items():
            if exclude_unset and value is None:
                continue
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await db.rollback()
            raise ValueError(f"Update failed due to integrity error: {e}") from e

    async def remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        obj = await self.get(db, id=id)
        if not obj:
            return None
        await db.delete(obj)
        await db.commit()
        return obj

    async def soft_remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        obj = await self.get(db, id=id)
        if not obj:
            return None
        if not hasattr(obj, "is_delete"):
            # 没有软删除字段就硬删
            await db.delete(obj)
            await db.commit()
            return obj
        setattr(obj, "is_delete", True)
        await db.commit()
        await db.refresh(obj)
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
