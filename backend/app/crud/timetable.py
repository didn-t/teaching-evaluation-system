# app/crud/timetable.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Timetable  # 按你的实际路径改


class CRUDTimetable(CRUDBase[Timetable]):
    def find_existing_for_upsert(self, db: Session, *, payload: Dict[str, Any]) -> Optional[Timetable]:
        sync_source = int(payload.get("sync_source", 0) or 0)
        external_id = payload.get("external_id")

        # 1) 教务来源幂等：sync_source + external_id
        if sync_source != 0 and external_id:
            stmt = select(Timetable).where(
                Timetable.sync_source == sync_source,
                Timetable.external_id == external_id,
            )
            return db.execute(stmt).scalars().first()

        # 2) 手工来源幂等：按 uk_timetable_slot
        keys = [
            Timetable.academic_year == payload["academic_year"],
            Timetable.semester == payload["semester"],
            Timetable.teacher_id == payload["teacher_id"],
            Timetable.class_name == payload["class_name"],
            Timetable.course_name == payload["course_name"],
            Timetable.weekday == payload["weekday"],
            Timetable.period == payload["period"],
            Timetable.section_time == payload["section_time"],
            Timetable.week_info == payload["week_info"],
            Timetable.classroom == payload.get("classroom", "") or "",
        ]
        stmt = select(Timetable).where(and_(*keys))
        return db.execute(stmt).scalars().first()

    def upsert(self, db: Session, *, payload: Dict[str, Any]) -> Timetable:
        """
        payload 需要包含：academic_year, semester, teacher_id, class_name, course_name,
                        weekday, period, section_time, week_info
        其他字段可选。
        """
        existing = self.find_existing_for_upsert(db, payload=payload)
        if existing:
            # 更新（不覆盖 is_delete，避免把已软删的“复活”除非你明确要）
            safe_payload = dict(payload)
            safe_payload.pop("is_delete", None)
            return self.update(db, db_obj=existing, obj_in=safe_payload, exclude_unset=True)

        # 新建
        if "classroom" not in payload or payload["classroom"] is None:
            payload["classroom"] = ""
        if "sync_source" not in payload or payload["sync_source"] is None:
            payload["sync_source"] = 0
        if "sync_status" not in payload or payload["sync_status"] is None:
            payload["sync_status"] = 1
        if "is_delete" not in payload:
            payload["is_delete"] = False

        return self.create(db, obj_in=payload)

    def list_by_teacher(
        self,
        db: Session,
        *,
        teacher_id: int,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
        include_deleted: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Timetable]:
        filters: List[Any] = [Timetable.teacher_id == teacher_id]
        if academic_year:
            filters.append(Timetable.academic_year == academic_year)
        if semester:
            filters.append(Timetable.semester == semester)

        return self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=[Timetable.weekday.asc(), Timetable.period.asc(), Timetable.section_time.asc()],
            include_deleted=include_deleted,
        )

    def list_by_class_name(
        self,
        db: Session,
        *,
        class_name: str,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
        include_deleted: bool = False,
    ) -> List[Timetable]:
        filters: List[Any] = [Timetable.class_name == class_name]
        if academic_year:
            filters.append(Timetable.academic_year == academic_year)
        if semester:
            filters.append(Timetable.semester == semester)

        return self.get_multi(
            db,
            skip=0,
            limit=10_000,
            filters=filters,
            order_by=[Timetable.weekday.asc(), Timetable.period.asc()],
            include_deleted=include_deleted,
        )


timetable_crud = CRUDTimetable(Timetable)
