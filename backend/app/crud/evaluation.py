from __future__ import annotations

import uuid
from datetime import datetime
from statistics import mean
from collections import Counter
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import TeachingEvaluation, Timetable, User, College, EvaluationDimension


class TeachingEvaluationCRUD:
    # ------- 工具方法 -------
    @staticmethod
    def generate_evaluation_no() -> str:
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        uid = uuid.uuid4().hex[:8].upper()
        return f"EVAL-{ts}-{uid}"

    @staticmethod
    def score_level(total_score: int) -> str:
        if total_score >= 90:
            return "优秀"
        if total_score >= 75:
            return "良好"
        if total_score >= 60:
            return "合格"
        return "不合格"

    # ------- 基础查询 -------
    async def get_timetable(self, db: AsyncSession, *, timetable_id: int) -> Optional[Timetable]:
        res = await db.execute(select(Timetable).where(Timetable.id == timetable_id))
        return res.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, *, evaluation_id: int) -> Optional[TeachingEvaluation]:
        from sqlalchemy.orm import selectinload
        res = await db.execute(
            select(TeachingEvaluation).where(
                TeachingEvaluation.id == evaluation_id,
                TeachingEvaluation.is_delete == False,
            ).options(
                selectinload(TeachingEvaluation.teach_teacher),
                selectinload(TeachingEvaluation.listen_teacher)
            )
        )
        return res.scalar_one_or_none()

    async def get_dimensions(self, db: AsyncSession) -> List[EvaluationDimension]:
        res = await db.execute(
            select(EvaluationDimension)
            .where(
                EvaluationDimension.status == 1,
                EvaluationDimension.is_delete == False,  # noqa: E712
            )
            .order_by(EvaluationDimension.sort_order)
        )
        return list(res.scalars().all())

    async def is_duplicate(
        self,
        db: AsyncSession,
        *,
        timetable_id: int,
        listen_teacher_id: int,
        listen_date: datetime,
    ) -> bool:
        stmt = select(TeachingEvaluation.id).where(
            TeachingEvaluation.timetable_id == timetable_id,
            TeachingEvaluation.listen_teacher_id == listen_teacher_id,
            TeachingEvaluation.listen_date == listen_date,
            TeachingEvaluation.is_delete == False,  # noqa: E712
        )
        res = await db.execute(stmt)
        return res.first() is not None

    # ------- 创建评教 -------
    async def submit(
        self,
        db: AsyncSession,
        *,
        timetable_id: int,
        listen_teacher_id: int,
        eval_source: Optional[str] = None,
        total_score: int,
        dimension_scores: Dict[str, Any],
        listen_date: datetime,
        advantage_content: Optional[str] = None,
        problem_content: Optional[str] = None,
        improve_suggestion: Optional[str] = None,
        listen_duration: Optional[int] = None,
        listen_location: Optional[str] = None,
        is_anonymous: bool = False,
        status: int = 1,
    ) -> TeachingEvaluation:
        timetable = await self.get_timetable(db, timetable_id=timetable_id)
        if not timetable:
            raise ValueError("课表不存在")

        if timetable.teacher_id == listen_teacher_id:
            raise ValueError("不能对自己教授的课程进行评教")

        if await self.is_duplicate(
            db,
            timetable_id=timetable_id,
            listen_teacher_id=listen_teacher_id,
            listen_date=listen_date,
        ):
            raise ValueError("该课表今日已由您评教，请勿重复提交")

        ev = TeachingEvaluation(
            evaluation_no=self.generate_evaluation_no(),
            timetable_id=timetable_id,
            teach_teacher_id=timetable.teacher_id,
            listen_teacher_id=listen_teacher_id,
            eval_source=eval_source,
            total_score=total_score,
            dimension_scores=dimension_scores,
            score_level=self.score_level(total_score),
            advantage_content=advantage_content,
            problem_content=problem_content,
            improve_suggestion=improve_suggestion,
            listen_date=listen_date,
            listen_duration=listen_duration,
            listen_location=listen_location,
            is_anonymous=is_anonymous,
            status=status,
            submit_time=datetime.utcnow(),
            is_delete=False,
        )

        db.add(ev)
        try:
            await db.commit()
            await db.refresh(ev)
            return ev
        except Exception as e:
            await db.rollback()
            raise ValueError(f"提交评教失败: {e}") from e

    # ------- 列表：我提交的（listen_teacher_id） -------
    async def list_mine(
        self,
        db: AsyncSession,
        *,
        listen_teacher_id: int,
        page: int = 1,
        page_size: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[int] = None,
    ) -> Tuple[List[TeachingEvaluation], int]:
        skip = (page - 1) * page_size
        conditions: List[Any] = [
            TeachingEvaluation.listen_teacher_id == listen_teacher_id,
            TeachingEvaluation.is_delete == False,  # noqa: E712
        ]
        if start_date:
            conditions.append(TeachingEvaluation.listen_date >= start_date)
        if end_date:
            conditions.append(TeachingEvaluation.listen_date <= end_date)
        if status is not None:
            conditions.append(TeachingEvaluation.status == status)

        # 22300417陈俫坤开发：为“我的评教”列表补齐课程名/授课教师名，避免前端只能展示评教编号
        base = (
            select(TeachingEvaluation)
            .options(
                selectinload(TeachingEvaluation.timetable),
                selectinload(TeachingEvaluation.teach_teacher),
            )
            .where(and_(*conditions))
        )
        res = await db.execute(
            base.order_by(TeachingEvaluation.submit_time.desc()).offset(skip).limit(page_size)
        )
        items = list(res.scalars().all())

        count_subq = base.with_only_columns(TeachingEvaluation.id).subquery()
        total = int((await db.execute(select(func.count()).select_from(count_subq))).scalar_one())
        return items, total

    # ------- 列表：某教师收到的（teach_teacher_id），支持筛选学年学期 -------
    async def list_by_teacher(
        self,
        db: AsyncSession,
        *,
        teach_teacher_id: int,
        page: int = 1,
        page_size: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        score_level: Optional[str] = None,
        status: Optional[int] = None,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> Tuple[List[TeachingEvaluation], int]:
        skip = (page - 1) * page_size

        conditions: List[Any] = [
            TeachingEvaluation.teach_teacher_id == teach_teacher_id,
            TeachingEvaluation.is_delete == False,  # noqa: E712
        ]
        if start_date:
            conditions.append(TeachingEvaluation.listen_date >= start_date)
        if end_date:
            conditions.append(TeachingEvaluation.listen_date <= end_date)
        if score_level:
            conditions.append(TeachingEvaluation.score_level == score_level)
        if status is not None:
            conditions.append(TeachingEvaluation.status == status)

        base = (
            select(TeachingEvaluation)
            .join(Timetable, TeachingEvaluation.timetable_id == Timetable.id)
            .options(
                selectinload(TeachingEvaluation.timetable),
                selectinload(TeachingEvaluation.listen_teacher),
                selectinload(TeachingEvaluation.teach_teacher),
            )
            .where(and_(*conditions))
        )
        if academic_year and semester:
            base = base.where(Timetable.academic_year == academic_year, Timetable.semester == semester)

        res = await db.execute(
            base.order_by(TeachingEvaluation.submit_time.desc()).offset(skip).limit(page_size)
        )
        items = list(res.scalars().all())

        count_subq = base.with_only_columns(TeachingEvaluation.id).subquery()
        total = int((await db.execute(select(func.count()).select_from(count_subq))).scalar_one())
        return items, total

    async def list_by_timetable(self, db: AsyncSession, *, timetable_id: int) -> List[TeachingEvaluation]:
        res = await db.execute(
            select(TeachingEvaluation)
            .where(
                TeachingEvaluation.timetable_id == timetable_id,
                TeachingEvaluation.is_delete == False,  # noqa: E712
            )
            .order_by(TeachingEvaluation.submit_time.desc())
            .options(
                selectinload(TeachingEvaluation.listen_teacher),
                selectinload(TeachingEvaluation.teach_teacher),
            )
        )
        return list(res.scalars().all())

    # ------- 软删除 -------
    async def soft_delete(self, db: AsyncSession, *, evaluation_id: int) -> bool:
        ev = await self.get_by_id(db, evaluation_id=evaluation_id)
        if not ev:
            return False
        ev.is_delete = True
        await db.commit()
        return True

    # ------- 审核/状态更新 -------
    async def update_status(
        self,
        db: AsyncSession,
        *,
        evaluation_id: int,
        status: int,
        review_comment: Optional[str] = None,
    ) -> Optional[TeachingEvaluation]:
        ev = await self.get_by_id(db, evaluation_id=evaluation_id)
        if not ev:
            return None
        ev.status = status
        if review_comment is not None and hasattr(ev, "review_comment"):
            ev.review_comment = review_comment
        try:
            await db.commit()
            await db.refresh(ev)
            return ev
        except Exception:
            await db.rollback()
            raise

    # ------- 统计：教师（修正 join 学年学期过滤 + 高频） -------
    async def teacher_statistics(
        self,
        db: AsyncSession,
        *,
        teacher_id: int,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> Dict[str, Any]:
        teacher = (await db.execute(select(User).where(User.id == teacher_id))).scalar_one_or_none()
        if not teacher:
            raise ValueError("教师不存在")

        stmt = (
            select(TeachingEvaluation)
            .join(Timetable, TeachingEvaluation.timetable_id == Timetable.id)
            .where(
                TeachingEvaluation.teach_teacher_id == teacher_id,
                TeachingEvaluation.is_delete == False,  # noqa: E712
                TeachingEvaluation.status == 1,  # 只算有效
            )
        )
        if academic_year and semester:
            stmt = stmt.where(Timetable.academic_year == academic_year, Timetable.semester == semester)

        evaluations = list((await db.execute(stmt)).scalars().all())
        scores = [e.total_score for e in evaluations]

        # 22300417陈俫坤开发：补齐待审核/总数统计口径（用于个人统计页展示）
        pending_stmt = (
            select(func.count(TeachingEvaluation.id))
            .join(Timetable, TeachingEvaluation.timetable_id == Timetable.id)
            .where(
                TeachingEvaluation.teach_teacher_id == teacher_id,
                TeachingEvaluation.is_delete == False,  # noqa: E712
                TeachingEvaluation.status == 2,
            )
        )
        if academic_year and semester:
            pending_stmt = pending_stmt.where(Timetable.academic_year == academic_year, Timetable.semester == semester)
        pending_evaluation_num = int((await db.execute(pending_stmt)).scalar_one() or 0)
        valid_evaluation_num = int(len(evaluations))
        total_evaluations = int(valid_evaluation_num + pending_evaluation_num)

        college_name = None
        if teacher.college_id:
            college = (await db.execute(select(College).where(College.id == teacher.college_id))).scalar_one_or_none()
            college_name = college.college_name if college else None

        # 22300417陈俫坤开发：评教趋势（按月份聚合平均分，只统计有效评教）
        trend_map: Dict[str, List[int]] = {}
        for ev in evaluations:
            dt = ev.listen_date or ev.submit_time
            try:
                label = dt.strftime("%Y-%m") if dt else ""
            except Exception:
                label = ""
            if not label:
                continue
            trend_map.setdefault(label, []).append(int(ev.total_score or 0))
        trend_data = [
            {"label": k, "score": round(mean(v), 1) if v else 0.0}
            for k, v in sorted(trend_map.items(), key=lambda x: x[0])
        ]

        # 22300417陈俫坤开发：维度名映射（前端提交的维度 key -> 数据库维度 code/name）
        dim_code_map = {
            "teachingAttitude": "teaching_attitude",
            "content": "teaching_content",
            "method": "teaching_method",
            "effect": "teaching_effect",
        }
        dim_fallback_name = {
            "teachingAttitude": "教学态度",
            "content": "教学内容",
            "method": "教学方法与手段",
            "effect": "教学效果",
        }
        dim_rows = await db.execute(
            select(EvaluationDimension.dimension_code, EvaluationDimension.dimension_name)
            .where(EvaluationDimension.is_delete == False, EvaluationDimension.status == 1)  # noqa: E712
        )
        dim_name_by_code = {r[0]: r[1] for r in dim_rows.all() if r and r[0]}

        if not evaluations:
            empty_dimension_scores = [
                {
                    "dimension_code": dim_code_map[k],
                    "dimension_key": k,
                    "dimension_name": dim_name_by_code.get(dim_code_map[k], dim_fallback_name.get(k, k)),
                    "score": 0.0,
                }
                for k in ("teachingAttitude", "content", "method", "effect")
            ]
            return {
                "teacher_id": teacher_id,
                "teacher_name": teacher.user_name,
                "college_id": teacher.college_id,
                "college_name": college_name,
                "total_evaluations": total_evaluations,
                "valid_evaluation_num": valid_evaluation_num,
                "pending_evaluation_num": pending_evaluation_num,
                "total_evaluation_num": valid_evaluation_num,
                "avg_total_score": 0.0,
                "max_score": None,
                "min_score": None,
                "dimension_avg_scores": None,
                "dimension_scores": empty_dimension_scores,
                "trend_data": trend_data,
                "score_distribution": {"优秀": 0, "良好": 0, "合格": 0, "不合格": 0},
                "high_freq_problems": None,
                "high_freq_suggestions": None,
            }

        score_distribution = {
            "优秀": sum(1 for s in scores if s >= 90),
            "良好": sum(1 for s in scores if 75 <= s < 90),
            "合格": sum(1 for s in scores if 60 <= s < 75),
            "不合格": sum(1 for s in scores if s < 60),
        }

        # 维度平均分（dimension_scores 视为 dict）
        dimension_scores_list = [e.dimension_scores for e in evaluations if isinstance(e.dimension_scores, dict)]
        dimension_avg_scores: Dict[str, float] = {}
        if dimension_scores_list:
            all_keys = set().union(*[ds.keys() for ds in dimension_scores_list])
            for k in all_keys:
                vals = [float(ds.get(k, 0) or 0) for ds in dimension_scores_list]
                dimension_avg_scores[k] = round(mean(vals), 2) if vals else 0.0

        dimension_scores = [
            {
                "dimension_code": dim_code_map[k],
                "dimension_key": k,
                "dimension_name": dim_name_by_code.get(dim_code_map[k], dim_fallback_name.get(k, k)),
                "score": float(dimension_avg_scores.get(k, 0) or 0),
            }
            for k in ("teachingAttitude", "content", "method", "effect")
        ]

        problems = [e.problem_content.strip() for e in evaluations if e.problem_content and e.problem_content.strip()]
        suggestions = [e.improve_suggestion.strip() for e in evaluations if e.improve_suggestion and e.improve_suggestion.strip()]
        high_freq_problems = [t for t, _ in Counter(problems).most_common(5)] if problems else None
        high_freq_suggestions = [t for t, _ in Counter(suggestions).most_common(5)] if suggestions else None

        return {
            "teacher_id": teacher_id,
            "teacher_name": teacher.user_name,
            "college_id": teacher.college_id,
            "college_name": college_name,
            "total_evaluations": total_evaluations,
            "valid_evaluation_num": valid_evaluation_num,
            "pending_evaluation_num": pending_evaluation_num,
            "total_evaluation_num": valid_evaluation_num,
            "avg_total_score": round(mean(scores), 2) if scores else 0.0,
            "max_score": max(scores),
            "min_score": min(scores),
            "dimension_avg_scores": dimension_avg_scores or None,
            "dimension_scores": dimension_scores,
            "trend_data": trend_data,
            "score_distribution": score_distribution,
            "high_freq_problems": high_freq_problems,
            "high_freq_suggestions": high_freq_suggestions,
        }

    # ------- 统计：听课人（我提交的评教统计） -------
    async def listen_statistics(
        self,
        db: AsyncSession,
        *,
        listen_teacher_id: int,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> Dict[str, Any]:
        listener = (await db.execute(select(User).where(User.id == listen_teacher_id))).scalar_one_or_none()
        if not listener:
            raise ValueError("用户不存在")

        stmt = (
            select(TeachingEvaluation)
            .join(Timetable, TeachingEvaluation.timetable_id == Timetable.id)
            .where(
                TeachingEvaluation.listen_teacher_id == listen_teacher_id,
                TeachingEvaluation.is_delete == False,  # noqa: E712
                TeachingEvaluation.status == 1,
            )
        )
        if academic_year and semester:
            stmt = stmt.where(Timetable.academic_year == academic_year, Timetable.semester == semester)

        evaluations = list((await db.execute(stmt)).scalars().all())
        scores = [e.total_score for e in evaluations]

        pending_stmt = (
            select(func.count(TeachingEvaluation.id))
            .join(Timetable, TeachingEvaluation.timetable_id == Timetable.id)
            .where(
                TeachingEvaluation.listen_teacher_id == listen_teacher_id,
                TeachingEvaluation.is_delete == False,  # noqa: E712
                TeachingEvaluation.status == 2,
            )
        )
        if academic_year and semester:
            pending_stmt = pending_stmt.where(Timetable.academic_year == academic_year, Timetable.semester == semester)
        pending_evaluation_num = int((await db.execute(pending_stmt)).scalar_one() or 0)
        valid_evaluation_num = int(len(evaluations))
        total_evaluations = int(valid_evaluation_num + pending_evaluation_num)

        trend_map: Dict[str, List[int]] = {}
        for ev in evaluations:
            dt = ev.listen_date or ev.submit_time
            try:
                label = dt.strftime("%Y-%m") if dt else ""
            except Exception:
                label = ""
            if not label:
                continue
            trend_map.setdefault(label, []).append(int(ev.total_score or 0))
        trend_data = [
            {"label": k, "score": round(mean(v), 1) if v else 0.0}
            for k, v in sorted(trend_map.items(), key=lambda x: x[0])
        ]

        dim_code_map = {
            "teachingAttitude": "teaching_attitude",
            "content": "teaching_content",
            "method": "teaching_method",
            "effect": "teaching_effect",
        }
        dim_fallback_name = {
            "teachingAttitude": "教学态度",
            "content": "教学内容",
            "method": "教学方法与手段",
            "effect": "教学效果",
        }
        dim_rows = await db.execute(
            select(EvaluationDimension.dimension_code, EvaluationDimension.dimension_name)
            .where(EvaluationDimension.is_delete == False, EvaluationDimension.status == 1)  # noqa: E712
        )
        dim_name_by_code = {r[0]: r[1] for r in dim_rows.all() if r and r[0]}

        dimension_scores_list = [e.dimension_scores for e in evaluations if isinstance(e.dimension_scores, dict)]
        dimension_avg_scores: Dict[str, float] = {}
        if dimension_scores_list:
            all_keys = set().union(*[ds.keys() for ds in dimension_scores_list])
            for k in all_keys:
                vals = [float(ds.get(k, 0) or 0) for ds in dimension_scores_list]
                dimension_avg_scores[k] = round(mean(vals), 2) if vals else 0.0

        dimension_scores = [
            {
                "dimension_code": dim_code_map[k],
                "dimension_key": k,
                "dimension_name": dim_name_by_code.get(dim_code_map[k], dim_fallback_name.get(k, k)),
                "score": float(dimension_avg_scores.get(k, 0) or 0),
            }
            for k in ("teachingAttitude", "content", "method", "effect")
        ]

        return {
            "listen_teacher_id": listen_teacher_id,
            "listen_teacher_name": listener.user_name,
            "total_evaluations": total_evaluations,
            "valid_evaluation_num": valid_evaluation_num,
            "pending_evaluation_num": pending_evaluation_num,
            "total_evaluation_num": valid_evaluation_num,
            "avg_total_score": round(mean(scores), 2) if scores else 0.0,
            "dimension_avg_scores": dimension_avg_scores or None,
            "dimension_scores": dimension_scores,
            "trend_data": trend_data,
        }

    async def listen_statistics_supervisor(
        self,
        db: AsyncSession,
        *,
        listen_teacher_id: int,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> Dict[str, Any]:
        """22300417陈俫坤开发：督导“我提交的评教”统计（聚合增强）"""

        listener = (await db.execute(select(User).where(User.id == listen_teacher_id))).scalar_one_or_none()
        if not listener:
            raise ValueError("用户不存在")

        base_where = [
            TeachingEvaluation.listen_teacher_id == listen_teacher_id,
            TeachingEvaluation.is_delete == False,  # noqa: E712
            TeachingEvaluation.status == 1,
            # 22300417陈俫坤开发：督导统计仅统计督导评教（兼容旧数据 eval_source 为空）
            or_(TeachingEvaluation.eval_source == "supervisor", TeachingEvaluation.eval_source.is_(None)),
        ]

        stmt = (
            select(
                TeachingEvaluation.total_score,
                TeachingEvaluation.teach_teacher_id,
                User.user_name,
                Timetable.college_id,
                College.college_name,
            )
            .join(Timetable, TeachingEvaluation.timetable_id == Timetable.id)
            .join(User, User.id == TeachingEvaluation.teach_teacher_id)
            .outerjoin(College, College.id == Timetable.college_id)
            .where(and_(*base_where))
        )
        if academic_year and semester:
            stmt = stmt.where(Timetable.academic_year == academic_year, Timetable.semester == semester)

        rows = list((await db.execute(stmt)).all())
        scores = [int(r[0] or 0) for r in rows]

        pending_stmt = (
            select(func.count(TeachingEvaluation.id))
            .join(Timetable, TeachingEvaluation.timetable_id == Timetable.id)
            .where(
                TeachingEvaluation.listen_teacher_id == listen_teacher_id,
                TeachingEvaluation.is_delete == False,  # noqa: E712
                TeachingEvaluation.status == 2,
                or_(TeachingEvaluation.eval_source == "supervisor", TeachingEvaluation.eval_source.is_(None)),
            )
        )
        if academic_year and semester:
            pending_stmt = pending_stmt.where(Timetable.academic_year == academic_year, Timetable.semester == semester)
        pending_evaluation_num = int((await db.execute(pending_stmt)).scalar_one() or 0)

        valid_evaluation_num = int(len(rows))
        total_evaluations = int(valid_evaluation_num + pending_evaluation_num)

        def level5(score: int) -> str:
            if score >= 90:
                return "优秀"
            if score >= 80:
                return "良好"
            if score >= 70:
                return "一般"
            if score >= 60:
                return "合格"
            return "不合格"

        college_map: Dict[int, Dict[str, Any]] = {}
        level_teacher_map: Dict[str, Dict[tuple[int, int], Dict[str, Any]]] = {
            "优秀": {},
            "良好": {},
            "一般": {},
            "合格": {},
            "不合格": {},
        }

        for total_score, teach_teacher_id, teach_teacher_name, cid, cname in rows:
            cidi = int(cid) if cid is not None else 0
            cn = cname or "未知学院"
            tid = int(teach_teacher_id) if teach_teacher_id is not None else 0
            tn = teach_teacher_name or "未知教师"
            score_int = int(total_score or 0)

            cobj = college_map.get(cidi)
            if cobj is None:
                cobj = {
                    "college_id": cidi,
                    "college_name": cn,
                    "evaluation_count": 0,
                    "teachers": {},
                }
                college_map[cidi] = cobj
            cobj["evaluation_count"] += 1
            tmap = cobj["teachers"]
            tob = tmap.get(tid)
            if tob is None:
                tob = {"teacher_id": tid, "teacher_name": tn, "evaluation_count": 0}
                tmap[tid] = tob
            tob["evaluation_count"] += 1

            lv = level5(score_int)
            key = (cidi, tid)
            lmap = level_teacher_map[lv]
            lob = lmap.get(key)
            if lob is None:
                lob = {
                    "college_id": cidi,
                    "college_name": cn,
                    "teacher_id": tid,
                    "teacher_name": tn,
                    "evaluation_count": 0,
                }
                lmap[key] = lob
            lob["evaluation_count"] += 1

        college_stats = []
        for _, cobj in sorted(college_map.items(), key=lambda x: (-int(x[1].get("evaluation_count", 0)), x[1].get("college_name", ""))):
            teachers = list(cobj["teachers"].values())
            teachers.sort(key=lambda x: (-int(x.get("evaluation_count", 0)), x.get("teacher_name", "")))
            college_stats.append(
                {
                    "college_id": cobj["college_id"],
                    "college_name": cobj["college_name"],
                    "evaluation_count": int(cobj["evaluation_count"]),
                    "teacher_count": int(len(teachers)),
                    "teachers": teachers,
                }
            )

        level_stats = {}
        for lv in ("优秀", "良好", "一般", "合格", "不合格"):
            items = list(level_teacher_map[lv].values())
            items.sort(key=lambda x: (-int(x.get("evaluation_count", 0)), x.get("college_name", ""), x.get("teacher_name", "")))
            level_stats[lv] = {
                "count": int(sum(int(x.get("evaluation_count", 0)) for x in items)),
                "teachers": items,
            }

        return {
            "listen_teacher_id": listen_teacher_id,
            "listen_teacher_name": listener.user_name,
            "total_evaluations": total_evaluations,
            "valid_evaluation_num": valid_evaluation_num,
            "pending_evaluation_num": pending_evaluation_num,
            "total_evaluation_num": valid_evaluation_num,
            "avg_total_score": round(mean(scores), 2) if scores else 0.0,
            "college_stats": college_stats,
            "level_stats": level_stats,
        }


evaluation_crud = TeachingEvaluationCRUD()
