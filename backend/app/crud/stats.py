# app/crud/stats.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Timetable,
    TeachingEvaluation,
    TeacherEvaluationStat,
    CollegeEvaluationStat,
    User,
    College,
    EvaluationDimension,
)


async def recompute_teacher_stat(db: AsyncSession, *, teacher_id: int, stat_year: str, stat_semester: int) -> TeacherEvaluationStat:
    # 先找本学期该教师涉及的课表
    tt_ids_stmt = select(Timetable.id, Timetable.college_id).where(
        Timetable.teacher_id == teacher_id,
        Timetable.academic_year == stat_year,
        Timetable.semester == stat_semester,
        Timetable.is_delete == False,  # noqa: E712
    )
    rows = (await db.execute(tt_ids_stmt)).all()
    timetable_ids = [r[0] for r in rows]
    # college_id：这里用“最多出现的college_id”或第一条；你也可强制 teacher_profile/college_id
    college_id = next((r[1] for r in rows if r[1] is not None), None)

    # 没有课表就清空/创建空统计
    if not timetable_ids:
        stat = (await db.execute(select(TeacherEvaluationStat).where(
            TeacherEvaluationStat.teacher_id == teacher_id,
            TeacherEvaluationStat.stat_year == stat_year,
            TeacherEvaluationStat.stat_semester == stat_semester,
        ))).scalars().first()
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
        await db.commit()
        await db.refresh(stat)
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
    total_num, avg_score, max_score, min_score = (await db.execute(agg_stmt)).one()

    stat = (await db.execute(select(TeacherEvaluationStat).where(
        TeacherEvaluationStat.teacher_id == teacher_id,
        TeacherEvaluationStat.stat_year == stat_year,
        TeacherEvaluationStat.stat_semester == stat_semester,
    ))).scalars().first()

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

    # dimension_avg_scores：计算各维度平均分
    dim_scores_stmt = select(TeachingEvaluation.dimension_scores).where(
        TeachingEvaluation.timetable_id.in_(timetable_ids),
        TeachingEvaluation.status == 1,
        TeachingEvaluation.is_delete == False,  # noqa: E712
    )
    dim_scores_results = await db.execute(dim_scores_stmt)
    dim_scores_list = [r[0] for r in dim_scores_results if r[0] is not None]
    
    if dim_scores_list:
        # 合并所有维度
        all_dims = set()
        for dim_scores in dim_scores_list:
            if isinstance(dim_scores, dict):
                all_dims.update(dim_scores.keys())
        
        # 计算各维度平均分
        dim_avg_scores = {}
        for dim in all_dims:
            scores = []
            for dim_scores in dim_scores_list:
                if isinstance(dim_scores, dict) and dim in dim_scores:
                    score = dim_scores[dim]
                    if isinstance(score, (int, float)):
                        scores.append(score)
            if scores:
                dim_avg_scores[dim] = float(sum(scores) / len(scores))
        
        stat.dimension_avg_scores = dim_avg_scores
    else:
        stat.dimension_avg_scores = None

    await db.commit()
    await db.refresh(stat)
    return stat


async def recompute_college_stat(db: AsyncSession, *, college_id: int, stat_year: str, stat_semester: int) -> CollegeEvaluationStat:
    # 找学院本学期课表
    tt_ids_stmt = select(Timetable.id).where(
        Timetable.college_id == college_id,
        Timetable.academic_year == stat_year,
        Timetable.semester == stat_semester,
        Timetable.is_delete == False,  # noqa: E712
    )
    timetable_ids = [r[0] for r in (await db.execute(tt_ids_stmt)).all()]

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
        total_eval, avg_score = (await db.execute(agg_stmt)).one()

    stat = (await db.execute(select(CollegeEvaluationStat).where(
        CollegeEvaluationStat.college_id == college_id,
        CollegeEvaluationStat.stat_year == stat_year,
        CollegeEvaluationStat.stat_semester == stat_semester,
    ))).scalars().first()

    if not stat:
        stat = CollegeEvaluationStat(
            college_id=college_id,
            stat_year=stat_year,
            stat_semester=stat_semester,
        )
        db.add(stat)

    stat.total_evaluation_num = int(total_eval or 0)
    stat.avg_total_score = float(avg_score) if avg_score is not None else None
    
    # 计算学院各维度平均分
    dim_scores_stmt = select(TeachingEvaluation.dimension_scores).where(
        TeachingEvaluation.timetable_id.in_(timetable_ids),
        TeachingEvaluation.status == 1,
        TeachingEvaluation.is_delete == False,  # noqa: E712
    )
    dim_scores_results = await db.execute(dim_scores_stmt)
    dim_scores_list = [r[0] for r in dim_scores_results if r[0] is not None]
    
    if dim_scores_list:
        # 合并所有维度
        all_dims = set()
        for dim_scores in dim_scores_list:
            if isinstance(dim_scores, dict):
                all_dims.update(dim_scores.keys())
        
        # 计算各维度平均分
        dim_avg_scores = {}
        for dim in all_dims:
            scores = []
            for dim_scores in dim_scores_list:
                if isinstance(dim_scores, dict) and dim in dim_scores:
                    score = dim_scores[dim]
                    if isinstance(score, (int, float)):
                        scores.append(score)
            if scores:
                dim_avg_scores[dim] = float(sum(scores) / len(scores))
        
        stat.dimension_avg_scores = dim_avg_scores
    else:
        stat.dimension_avg_scores = None

    await db.commit()
    await db.refresh(stat)
    return stat


async def get_college_statistics(db: AsyncSession, *, college_id: int, academic_year: Optional[str] = None, semester: Optional[int] = None) -> Dict[str, Any]:
    """获取学院评教统计"""
    # 获取学院信息
    college = await db.get(College, college_id)
    if not college:
        raise ValueError("学院不存在")
    
    # 获取学院教师列表
    teacher_stmt = select(User.id, User.user_name).where(
        User.college_id == college_id,
        User.is_delete == False,  # noqa: E712
    )
    teachers = await db.execute(teacher_stmt)
    teacher_list = [(t[0], t[1]) for t in teachers]
    
    # 获取学院评教数据
    evaluation_stmt = select(
        TeachingEvaluation,
        Timetable,
        User.user_name.label('teach_teacher_name')
    ).join(
        Timetable, TeachingEvaluation.timetable_id == Timetable.id
    ).join(
        User, Timetable.teacher_id == User.id
    ).where(
        Timetable.college_id == college_id,
        TeachingEvaluation.is_delete == False,  # noqa: E712
        TeachingEvaluation.status == 1,  # 只算有效
    )
    
    # 添加学年学期过滤
    if academic_year and semester:
        evaluation_stmt = evaluation_stmt.where(
            Timetable.academic_year == academic_year,
            Timetable.semester == semester
        )
    
    evaluations = await db.execute(evaluation_stmt)
    evaluation_list = evaluations.all()
    
    # 计算学院总平均分
    total_scores = [e[0].total_score for e in evaluation_list]
    college_avg_score = sum(total_scores) / len(total_scores) if total_scores else 0
    
    # 计算各教师平均分
    teacher_avg_scores = {}
    for teacher_id, teacher_name in teacher_list:
        teacher_evaluations = [e for e in evaluation_list if e[2] == teacher_name]
        if teacher_evaluations:
            teacher_scores = [e[0].total_score for e in teacher_evaluations]
            teacher_avg_scores[teacher_id] = {
                'name': teacher_name,
                'avg_score': sum(teacher_scores) / len(teacher_scores),
                'total_evaluations': len(teacher_evaluations),
                'max_score': max(teacher_scores),
                'min_score': min(teacher_scores)
            }
    
    # 计算得分分布
    score_levels = {"优秀": 0, "良好": 0, "合格": 0, "不合格": 0}
    for score in total_scores:
        if score >= 90:
            score_levels["优秀"] += 1
        elif score >= 75:
            score_levels["良好"] += 1
        elif score >= 60:
            score_levels["合格"] += 1
        else:
            score_levels["不合格"] += 1
    
    # 提取高频问题
    problems = []
    suggestions = []
    for e in evaluation_list:
        eval_item = e[0]
        if eval_item.problem_content:
            problems.append(eval_item.problem_content.strip())
        if eval_item.improve_suggestion:
            suggestions.append(eval_item.improve_suggestion.strip())
    
    # 统计高频问题
    def get_top_issues(items: List[str], top_n: int = 5) -> List[str]:
        from collections import Counter
        if not items:
            return []
        counter = Counter(items)
        return [issue for issue, _ in counter.most_common(top_n)]
    
    top_problems = get_top_issues(problems)
    top_suggestions = get_top_issues(suggestions)
    
    return {
        "college_id": college_id,
        "college_name": college.college_name,
        "academic_year": academic_year,
        "semester": semester,
        "total_evaluations": len(evaluation_list),
        "college_avg_score": college_avg_score,
        "teacher_avg_scores": teacher_avg_scores,
        "score_distribution": score_levels,
        "top_problems": top_problems,
        "top_suggestions": top_suggestions,
    }


async def get_school_statistics(db: AsyncSession, *, academic_year: Optional[str] = None, semester: Optional[int] = None) -> Dict[str, Any]:
    """获取全校评教统计"""
    # 获取所有学院列表
    college_stmt = select(College.id, College.college_name)
    colleges = await db.execute(college_stmt)
    college_list = [(c[0], c[1]) for c in colleges]
    
    # 获取全校评教数据
    evaluation_stmt = select(
        TeachingEvaluation,
        Timetable,
        User.user_name.label('teach_teacher_name'),
        College.college_name
    ).join(
        Timetable, TeachingEvaluation.timetable_id == Timetable.id
    ).join(
        User, Timetable.teacher_id == User.id
    ).join(
        College, Timetable.college_id == College.id
    ).where(
        TeachingEvaluation.is_delete == False,  # noqa: E712
        TeachingEvaluation.status == 1,  # 只算有效
    )
    
    # 添加学年学期过滤
    if academic_year and semester:
        evaluation_stmt = evaluation_stmt.where(
            Timetable.academic_year == academic_year,
            Timetable.semester == semester
        )
    
    evaluations = await db.execute(evaluation_stmt)
    evaluation_list = evaluations.all()
    
    # 计算全校总平均分
    total_scores = [e[0].total_score for e in evaluation_list]
    school_avg_score = sum(total_scores) / len(total_scores) if total_scores else 0
    
    # 计算各学院平均分
    college_avg_scores = {}
    for college_id, college_name in college_list:
        college_evaluations = [e for e in evaluation_list if e[3] == college_name]
        if college_evaluations:
            college_scores = [e[0].total_score for e in college_evaluations]
            college_avg_scores[college_id] = {
                'name': college_name,
                'avg_score': sum(college_scores) / len(college_scores),
                'total_evaluations': len(college_evaluations)
            }
    
    # 学院排名（按平均分）
    college_ranking = sorted(
        college_avg_scores.values(),
        key=lambda x: x['avg_score'],
        reverse=True
    )
    
    return {
        "academic_year": academic_year,
        "semester": semester,
        "total_evaluations": len(evaluation_list),
        "school_avg_score": school_avg_score,
        "college_avg_scores": college_avg_scores,
        "college_ranking": college_ranking,
    }


async def get_teacher_ranking(
    db: AsyncSession,
    *,
    college_id: Optional[int] = None,
    college_ids: Optional[List[int]] = None,
    academic_year: Optional[str] = None,
    semester: Optional[int] = None,
    course_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """22300417陈俫坤开发：获取教师排名，修复SQL查询问题"""
    try:
        # 22300417陈俫坤开发：以 TeachingEvaluation.teach_teacher_id 为准计算排名，避免课表 teacher_id 与评教记录不一致导致无数据
        ranking_stmt = (
            select(
                User.id,
                User.user_name,
                College.college_name,
                func.avg(TeachingEvaluation.total_score).label("avg_score"),
                func.count(TeachingEvaluation.id).label("evaluation_count"),
            )
            .select_from(TeachingEvaluation)
            .join(Timetable, TeachingEvaluation.timetable_id == Timetable.id)
            .join(User, TeachingEvaluation.teach_teacher_id == User.id)
            .join(College, Timetable.college_id == College.id)
            .where(
                TeachingEvaluation.is_delete == False,  # noqa: E712
                # 22300417陈俫坤开发：兼容“待审核(2)”状态，否则在未走审核流程时排名会为空
                TeachingEvaluation.status.in_([1, 2]),
                Timetable.is_delete == False,  # noqa: E712
                User.is_delete == False,  # noqa: E712
                College.is_delete == False,  # noqa: E712
            )
            .group_by(User.id, User.user_name, College.college_name)
        )

        # 添加过滤条件
        if college_id:
            ranking_stmt = ranking_stmt.where(Timetable.college_id == college_id)
        elif college_ids:
            ranking_stmt = ranking_stmt.where(Timetable.college_id.in_(college_ids))

        if academic_year:
            ranking_stmt = ranking_stmt.where(Timetable.academic_year == academic_year)

        if semester:
            ranking_stmt = ranking_stmt.where(Timetable.semester == semester)

        if course_type:
            ranking_stmt = ranking_stmt.where(Timetable.course_type == course_type)

        # 按平均分排序
        ranking_stmt = ranking_stmt.order_by(func.avg(TeachingEvaluation.total_score).desc())

        result = await db.execute(ranking_stmt)
        ranking = result.all()

        return [
            {
                "teacher_id": r[0],
                "teacher_name": r[1],
                "college_name": r[2],
                "avg_score": float(r[3]) if r[3] else 0,
                "evaluation_count": r[4],
            }
            for r in ranking
        ]

    except Exception as e:
        # 22300417陈俫坤开发：不要吞掉异常，让上层接口返回明确错误，便于定位
        print(f"教师排名查询失败: {e}")
        raise
