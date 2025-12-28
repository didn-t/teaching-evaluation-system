# app/crud/stats.py
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Timetable,
    TeachingEvaluation,
    TeacherEvaluationStat,
    CollegeEvaluationStat,
)


def recompute_teacher_stat(db: Session, *, teacher_id: int, stat_year: str, stat_semester: int) -> TeacherEvaluationStat:
    # 先找本学期该教师涉及的课表
    tt_ids_stmt = select(Timetable.id, Timetable.college_id).where(
        Timetable.teacher_id == teacher_id,
        Timetable.academic_year == stat_year,
        Timetable.semester == stat_semester,
        Timetable.is_delete == False,  # noqa: E712
    )
    rows = db.execute(tt_ids_stmt).all()
    timetable_ids = [r[0] for r in rows]
    # college_id：这里用“最多出现的college_id”或第一条；你也可强制 teacher_profile/college_id
    college_id = next((r[1] for r in rows if r[1] is not None), None)

    # 没有课表就清空/创建空统计
    if not timetable_ids:
        stat = db.execute(select(TeacherEvaluationStat).where(
            TeacherEvaluationStat.teacher_id == teacher_id,
            TeacherEvaluationStat.stat_year == stat_year,
            TeacherEvaluationStat.stat_semester == stat_semester,
        )).scalars().first()
        if not stat:
            stat = TeacherEvaluationStat(
                teacher_id=teacher_id,
                college_id=college_id or 0,
                stat_year=stat_year,
                stat_semester=stat_semester,
                total_evaluation_num=0,
            )
            db.add(stat)
        else:
            stat.total_evaluation_num = 0
            stat.avg_total_score = None
            stat.max_score = None
            stat.min_score = None
            stat.dimension_avg_scores = None
        db.commit()
        db.refresh(stat)
        return stat

    agg_stmt = select(
        func.count(TeachingEvaluation.id),
        func.avg(TeachingEvaluation.total_score),
        func.max(TeachingEvaluation.total_score),
        func.min(TeachingEvaluation.total_score),
    ).where(
        TeachingEvaluation.timetable_id.in_(timetable_ids),
        TeachingEvaluation.status == 1,
        TeachingEvaluation.is_delete == False,  # noqa: E712
    )
    total_num, avg_score, max_score, min_score = db.execute(agg_stmt).one()

    stat = db.execute(select(TeacherEvaluationStat).where(
        TeacherEvaluationStat.teacher_id == teacher_id,
        TeacherEvaluationStat.stat_year == stat_year,
        TeacherEvaluationStat.stat_semester == stat_semester,
    )).scalars().first()

    if not stat:
        stat = TeacherEvaluationStat(
            teacher_id=teacher_id,
            college_id=college_id or 0,
            stat_year=stat_year,
            stat_semester=stat_semester,
        )
        db.add(stat)

    if college_id is not None:
        stat.college_id = college_id

    stat.total_evaluation_num = int(total_num or 0)
    stat.avg_total_score = float(avg_score) if avg_score is not None else None
    stat.max_score = int(max_score) if max_score is not None else None
    stat.min_score = int(min_score) if min_score is not None else None

    # dimension_avg_scores：需要你定义 dimension_scores JSON 的结构
    # 这里先留空，你可以用 SQLAlchemy + JSON 函数或拉回内存计算
    stat.dimension_avg_scores = None

    db.commit()
    db.refresh(stat)
    return stat


def recompute_college_stat(db: Session, *, college_id: int, stat_year: str, stat_semester: int) -> CollegeEvaluationStat:
    # 找学院本学期课表
    tt_ids_stmt = select(Timetable.id).where(
        Timetable.college_id == college_id,
        Timetable.academic_year == stat_year,
        Timetable.semester == stat_semester,
        Timetable.is_delete == False,  # noqa: E712
    )
    timetable_ids = [r[0] for r in db.execute(tt_ids_stmt).all()]

    agg_stmt = select(
        func.count(TeachingEvaluation.id),
        func.avg(TeachingEvaluation.total_score),
    ).where(
        TeachingEvaluation.timetable_id.in_(timetable_ids) if timetable_ids else False,
        TeachingEvaluation.status == 1,
        TeachingEvaluation.is_delete == False,  # noqa: E712
    )

    total_eval, avg_score = (0, None)
    if timetable_ids:
        total_eval, avg_score = db.execute(agg_stmt).one()

    stat = db.execute(select(CollegeEvaluationStat).where(
        CollegeEvaluationStat.college_id == college_id,
        CollegeEvaluationStat.stat_year == stat_year,
        CollegeEvaluationStat.stat_semester == stat_semester,
    )).scalars().first()

    if not stat:
        stat = CollegeEvaluationStat(
            college_id=college_id,
            stat_year=stat_year,
            stat_semester=stat_semester,
        )
        db.add(stat)

    stat.total_evaluation_num = int(total_eval or 0)
    stat.avg_total_score = float(avg_score) if avg_score is not None else None
    stat.dimension_avg_scores = None
    stat.high_freq_problems = None
    stat.score_distribution = None
    stat.excellent_rate = None

    db.commit()
    db.refresh(stat)
    return stat
