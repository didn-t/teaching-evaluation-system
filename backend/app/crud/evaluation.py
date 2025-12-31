from __future__ import annotations

import uuid
from datetime import datetime
from statistics import mean
from collections import Counter
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy import select, func, and_
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

        base = select(TeachingEvaluation).where(and_(*conditions))
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

        college_name = None
        if teacher.college_id:
            college = (await db.execute(select(College).where(College.id == teacher.college_id))).scalar_one_or_none()
            college_name = college.college_name if college else None

        if not evaluations:
            return {
                "teacher_id": teacher_id,
                "teacher_name": teacher.user_name,
                "college_id": teacher.college_id,
                "college_name": college_name,
                "total_evaluation_num": 0,
                "avg_total_score": None,
                "max_score": None,
                "min_score": None,
                "dimension_avg_scores": None,
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

        problems = [e.problem_content.strip() for e in evaluations if e.problem_content and e.problem_content.strip()]
        suggestions = [e.improve_suggestion.strip() for e in evaluations if e.improve_suggestion and e.improve_suggestion.strip()]
        high_freq_problems = [t for t, _ in Counter(problems).most_common(5)] if problems else None
        high_freq_suggestions = [t for t, _ in Counter(suggestions).most_common(5)] if suggestions else None

        return {
            "teacher_id": teacher_id,
            "teacher_name": teacher.user_name,
            "college_id": teacher.college_id,
            "college_name": college_name,
            "total_evaluation_num": len(evaluations),
            "avg_total_score": round(mean(scores), 2),
            "max_score": max(scores),
            "min_score": min(scores),
            "dimension_avg_scores": dimension_avg_scores or None,
            "score_distribution": score_distribution,
            "high_freq_problems": high_freq_problems,
            "high_freq_suggestions": high_freq_suggestions,
        }


evaluation_crud = TeachingEvaluationCRUD()
