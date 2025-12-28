# app/crud/base.py
from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, Sequence, Type, TypeVar, Union

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, *, id: Any) -> Optional[ModelType]:
        return db.get(self.model, id)

    def get_multi(
        self,
        db: Session,
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

        # 默认排除软删除
        if not include_deleted and hasattr(self.model, "is_delete"):
            stmt = stmt.where(getattr(self.model, "is_delete") == False)  # noqa: E712

        if order_by:
            stmt = stmt.order_by(*order_by)

        stmt = stmt.offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def count(
        self,
        db: Session,
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

        return int(db.execute(stmt).scalar_one())

    def create(self, db: Session, *, obj_in: Union[Dict[str, Any], Any]) -> ModelType:
        data = obj_in if isinstance(obj_in, dict) else obj_in.__dict__
        db_obj = self.model(**data)  # type: ignore[arg-type]
        db.add(db_obj)
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Create failed due to integrity error: {e}") from e
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[Dict[str, Any], Any],
        exclude_unset: bool = True,
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.__dict__

        for field, value in update_data.items():
            if exclude_unset and value is None:
                continue
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Update failed due to integrity error: {e}") from e
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        obj = self.get(db, id=id)
        if not obj:
            return None
        db.delete(obj)
        db.commit()
        return obj

    def soft_remove(self, db: Session, *, id: Any) -> Optional[ModelType]:
        obj = self.get(db, id=id)
        if not obj:
            return None
        if not hasattr(obj, "is_delete"):
            # 没有软删除字段就硬删
            db.delete(obj)
            db.commit()
            return obj
        setattr(obj, "is_delete", True)
        db.commit()
        db.refresh(obj)
        return obj

    def restore(self, db: Session, *, id: Any) -> Optional[ModelType]:
        obj = self.get(db, id=id)
        if not obj:
            return None
        if hasattr(obj, "is_delete"):
            setattr(obj, "is_delete", False)
            db.commit()
            db.refresh(obj)
        return obj
