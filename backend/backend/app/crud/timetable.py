# app/crud/timetable.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import and_, select, func, true
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_async import CRUDBaseAsync
from app.models import Timetable, TeachingEvaluation


class CRUDTimetable(CRUDBaseAsync[Timetable]):
    async def find_existing_for_upsert(self, db: AsyncSession, *, payload: Dict[str, Any]) -> Optional[Timetable]:
        sync_source = int(payload.get("sync_source", 0) or 0)
        external_id = payload.get("external_id")

        # 1) 教务来源幂等：sync_source + external_id
        if sync_source != 0 and external_id:
            stmt = select(Timetable).where(
                Timetable.sync_source == sync_source,
                Timetable.external_id == external_id,
            )
            result = await db.execute(stmt)
            return result.scalars().first()

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
        result = await db.execute(stmt)
        return result.scalars().first()

    async def upsert(self, db: AsyncSession, *, payload: Dict[str, Any]) -> Timetable:
        """
        payload 需要包含：academic_year, semester, teacher_id, class_name, course_name,
                        weekday, period, section_time, week_info
        其他字段可选。
        """
        existing = await self.find_existing_for_upsert(db, payload=payload)
        if existing:
            # 更新（不覆盖 is_delete，避免把已软删的“复活”除非你明确要）
            safe_payload = dict(payload)
            safe_payload.pop("is_delete", None)
            return await self.update(db, db_obj=existing, obj_in=safe_payload, exclude_unset=True)

        # 新建
        if "classroom" not in payload or payload["classroom"] is None:
            payload["classroom"] = ""
        if "sync_source" not in payload or payload["sync_source"] is None:
            payload["sync_source"] = 0
        if "sync_status" not in payload or payload["sync_status"] is None:
            payload["sync_status"] = 1
        if "is_delete" not in payload:
            payload["is_delete"] = False

        return await self.create(db, obj_in=payload)

    async def list_by_teacher(
        self,
        db: AsyncSession,
        *,
        teacher_id: int,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
        include_deleted: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[List[Timetable], int]:
        filters: List[Any] = [Timetable.teacher_id == teacher_id]
        if academic_year:
            filters.append(Timetable.academic_year == academic_year)
        if semester:
            filters.append(Timetable.semester == semester)

        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=[Timetable.weekday.asc(), Timetable.period.asc(), Timetable.section_time.asc()],
            include_deleted=include_deleted,
        )

    async def list_by_class_name(
        self,
        db: AsyncSession,
        *,
        class_name: str,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
        include_deleted: bool = False,
    ) -> tuple[List[Timetable], int]:
        filters: List[Any] = [Timetable.class_name == class_name]
        if academic_year:
            filters.append(Timetable.academic_year == academic_year)
        if semester:
            filters.append(Timetable.semester == semester)

        return await self.get_multi(
            db,
            skip=0,
            limit=10_000,
            filters=filters,
            order_by=[Timetable.weekday.asc(), Timetable.period.asc()],
            include_deleted=include_deleted,
        )

    async def list_pending_evaluation(
        self,
        db: AsyncSession,
        *, 
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[Timetable], int]:
        """
        获取待评课程列表
        """
        filters: List[Any] = [
            Timetable.course_type == "待评"
        ]
        if academic_year:
            filters.append(Timetable.academic_year == academic_year)
        if semester:
            filters.append(Timetable.semester == semester)

        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=[Timetable.academic_year.desc(), Timetable.semester.desc()],
            include_deleted=include_deleted,
        )

    async def list_completed_evaluation_for_user(
        self,
        db: AsyncSession,
        *,
        listen_teacher_id: int,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[Timetable], int]:
        """22300417陈俫坤开发：按当前用户过滤已评课表

        规则：TeachingEvaluation 中存在 (timetable_id, listen_teacher_id) 的记录 => 该课表对该用户已评。
        注意：不依赖 Timetable.course_type（全局字段），避免“评教后仍显示待评”的问题。
        """

        filters: List[Any] = []
        if academic_year:
            filters.append(Timetable.academic_year == academic_year)
        if semester:
            filters.append(Timetable.semester == semester)
        if not include_deleted:
            filters.append(Timetable.is_delete == False)  # noqa: E712

        evaluated_exists = (
            select(TeachingEvaluation.id)
            .where(
                TeachingEvaluation.timetable_id == Timetable.id,
                TeachingEvaluation.listen_teacher_id == listen_teacher_id,
                TeachingEvaluation.is_delete == False,  # noqa: E712
            )
            .limit(1)
        )

        cond = and_(*filters) if filters else true()
        base = select(Timetable).where(cond, evaluated_exists.exists())

        res = await db.execute(
            base.order_by(Timetable.academic_year.desc(), Timetable.semester.desc())
            .offset(skip)
            .limit(limit)
        )
        items = list(res.scalars().all())

        count_subq = base.with_only_columns(Timetable.id).subquery()
        total = int((await db.execute(select(func.count()).select_from(count_subq))).scalar_one() or 0)
        return items, total

    async def list_pending_evaluation_for_user(
        self,
        db: AsyncSession,
        *,
        listen_teacher_id: int,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[Timetable], int]:
        """22300417陈俫坤开发：按当前用户过滤待评课表

        规则：
        1. 排除自己教授的课程（不能评教自己的课）
        2. 排除已评教过的课程
        3. 只显示当前学期或指定学期的课程
        """

        # 22300417陈俫坤开发：合理过滤待评课程
        filters: List[Any] = [
            Timetable.teacher_id != listen_teacher_id,  # 不能评教自己的课
        ]
        if academic_year:
            filters.append(Timetable.academic_year == academic_year)
        if semester:
            filters.append(Timetable.semester == semester)
        else:
            # 22300417陈俫坤开发：默认只显示当前学期课程，避免历史课程过多
            from datetime import datetime
            current_month = datetime.now().month
            current_semester = 1 if current_month <= 7 else 2  # 简单判断：1-7月为春季，8-12月为秋季
            filters.append(Timetable.semester == current_semester)
        if not include_deleted:
            filters.append(Timetable.is_delete == False)  # noqa: E712

        evaluated_exists = (
            select(TeachingEvaluation.id)
            .where(
                TeachingEvaluation.timetable_id == Timetable.id,
                TeachingEvaluation.listen_teacher_id == listen_teacher_id,
                TeachingEvaluation.is_delete == False,  # noqa: E712
            )
            .limit(1)
        )

        cond = and_(*filters) if filters else true()
        base = select(Timetable).where(cond, ~evaluated_exists.exists())

        res = await db.execute(
            base.order_by(Timetable.academic_year.desc(), Timetable.semester.desc())
            .offset(skip)
            .limit(limit)
        )
        items = list(res.scalars().all())

        count_subq = base.with_only_columns(Timetable.id).subquery()
        total = int((await db.execute(select(func.count()).select_from(count_subq))).scalar_one() or 0)
        return items, total

    async def list_completed_evaluation(
        self,
        db: AsyncSession,
        *, 
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
        skip: int = 0,
        limit: int = 10,
        include_deleted: bool = False,
    ) -> tuple[List[Timetable], int]:
        """
        获取已评课程列表
        """
        filters: List[Any] = [
            Timetable.course_type == "已评"
        ]
        if academic_year:
            filters.append(Timetable.academic_year == academic_year)
        if semester:
            filters.append(Timetable.semester == semester)

        return await self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=[Timetable.academic_year.desc(), Timetable.semester.desc()],
            include_deleted=include_deleted,
        )


    async def update_course_type(
        self,
        db: AsyncSession,
        *, 
        timetable_id: int,
        course_type: str
    ) -> Optional[Timetable]:
        """
        更新课程的评价状态
        """
        # 获取课程记录，自动过滤已删除记录
        timetable = await self.get(db, id=timetable_id)
        if not timetable:
            return None
        
        # 更新course_type
        timetable.course_type = course_type
        
        try:
            # 使用父类的update方法更新记录，确保异常处理一致
            updated_course = await self.update(
                db,
                db_obj=timetable,
                obj_in={"course_type": course_type}
            )
            return updated_course
        except Exception as e:
            # 记录错误信息
            print(f"更新课程评价状态失败: {e}")
            return None


timetable_crud = CRUDTimetable(Timetable)
