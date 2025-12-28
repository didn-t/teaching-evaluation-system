import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from statistics import mean
from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy import func, and_, or_

from app.models import (
    TeachingEvaluation, Timetable, User, College,
    EvaluationDimension, TeacherEvaluationStat, CollegeEvaluationStat
)
from app.schemas import EvaluationSubmit, TokenData


def generate_evaluation_no() -> str:
    """生成评教编号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8].upper()
    return f"EVAL-{timestamp}-{unique_id}"


def calculate_score_level(total_score: int) -> str:
    """根据总分计算等级"""
    if total_score >= 90:
        return "优秀"
    elif total_score >= 75:
        return "良好"
    elif total_score >= 60:
        return "合格"
    else:
        return "不合格"


async def get_timetable_by_id(db: AsyncSession, timetable_id: int) -> Optional[Timetable]:
    """根据课表ID获取课表信息"""
    try:
        result = await db.execute(select(Timetable).where(Timetable.id == timetable_id))
        return result.scalar_one_or_none()
    except NoResultFound:
        return None


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """根据用户ID获取用户信息"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    except NoResultFound:
        return None


async def check_duplicate_evaluation(
    db: AsyncSession,
    timetable_id: int,
    listen_teacher_id: int,
    listen_date: datetime
) -> bool:
    """检查是否重复评教（同一听课教师对同一课表同一天只能评教一次）"""
    try:
        result = await db.execute(
            select(TeachingEvaluation).where(
                TeachingEvaluation.timetable_id == timetable_id,
                TeachingEvaluation.listen_teacher_id == listen_teacher_id,
                TeachingEvaluation.listen_date == listen_date,
                TeachingEvaluation.is_delete == False
            )
        )
        existing = result.scalar_one_or_none()
        return existing is not None
    except NoResultFound:
        return False


async def create_evaluation(
    db: AsyncSession,
    submit_data: EvaluationSubmit,
    token_data: TokenData
) -> Optional[TeachingEvaluation]:
    """创建评教记录"""
    timetable = await get_timetable_by_id(db, submit_data.timetable_id)
    if not timetable:
        return None

    is_duplicate = await check_duplicate_evaluation(
        db,
        submit_data.timetable_id,
        token_data.id,
        submit_data.listen_date
    )
    if is_duplicate:
        raise ValueError("该课表今日已由您评教，请勿重复提交")

    evaluation_no = generate_evaluation_no()
    score_level = calculate_score_level(submit_data.total_score)

    evaluation = TeachingEvaluation(
        evaluation_no=evaluation_no,
        timetable_id=submit_data.timetable_id,
        teach_teacher_id=timetable.teacher_id,
        listen_teacher_id=token_data.id,
        total_score=submit_data.total_score,
        dimension_scores=submit_data.dimension_scores,
        score_level=score_level,
        advantage_content=submit_data.advantage_content,
        problem_content=submit_data.problem_content,
        improve_suggestion=submit_data.improve_suggestion,
        listen_date=submit_data.listen_date,
        listen_duration=submit_data.listen_duration,
        listen_location=submit_data.listen_location,
        is_anonymous=submit_data.is_anonymous,
        status=1,
        submit_time=datetime.now()
    )

    try:
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        return evaluation
    except Exception as e:
        print("创建评教记录失败", e)
        await db.rollback()
        return None


async def get_evaluation_by_id(db: AsyncSession, evaluation_id: int) -> Optional[TeachingEvaluation]:
    """根据评教ID获取评教记录"""
    try:
        result = await db.execute(
            select(TeachingEvaluation).where(
                TeachingEvaluation.id == evaluation_id,
                TeachingEvaluation.is_delete == False
            )
        )
        return result.scalar_one_or_none()
    except NoResultFound:
        return None


async def get_evaluation_dimensions(db: AsyncSession) -> List[EvaluationDimension]:
    """获取所有启用的评价维度配置"""
    result = await db.execute(
        select(EvaluationDimension).where(
            EvaluationDimension.status == 1,
        ).order_by(EvaluationDimension.sort_order)
    )
    return list(result.scalars().all())


async def get_evaluations_by_teacher(
    db: AsyncSession,
    teacher_id: int,
    page: int = 1,
    page_size: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    score_level: Optional[str] = None,
    status: Optional[int] = None
) -> tuple[List[TeachingEvaluation], int]:
    """根据教师ID获取评教记录列表"""
    skip = (page - 1) * page_size

    conditions = [
        TeachingEvaluation.teach_teacher_id == teacher_id,
        TeachingEvaluation.is_delete == False
    ]

    if start_date:
        conditions.append(TeachingEvaluation.listen_date >= start_date)
    if end_date:
        conditions.append(TeachingEvaluation.listen_date <= end_date)
    if score_level:
        conditions.append(TeachingEvaluation.score_level == score_level)
    if status is not None:
        conditions.append(TeachingEvaluation.status == status)

    result = await db.execute(
        select(TeachingEvaluation)
        .where(and_(*conditions))
        .order_by(TeachingEvaluation.submit_time.desc())
        .offset(skip)
        .limit(page_size)
    )
    evaluations = result.scalars().all()

    count_result = await db.execute(
        select(TeachingEvaluation.id).where(and_(*conditions))
    )
    total = len(count_result.all())

    return evaluations, total


async def get_evaluations_by_timetable(
    db: AsyncSession,
    timetable_id: int
) -> List[TeachingEvaluation]:
    """根据课表ID获取所有评教记录"""
    result = await db.execute(
        select(TeachingEvaluation)
        .where(
            TeachingEvaluation.timetable_id == timetable_id,
            TeachingEvaluation.is_delete == False
        )
        .order_by(TeachingEvaluation.submit_time.desc())
    )
    return list(result.scalars().all())


async def get_teacher_statistics(
    db: AsyncSession,
    teacher_id: int,
    academic_year: Optional[str] = None,
    semester: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """获取教师评教统计数据"""
    result = await db.execute(
        select(User).where(User.id == teacher_id)
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        return None

    conditions = [
        TeachingEvaluation.teach_teacher_id == teacher_id,
        TeachingEvaluation.is_delete == False,
        TeachingEvaluation.status == 1
    ]

    if academic_year and semester:
        result = await db.execute(
            select(Timetable).where(Timetable.id == TeachingEvaluation.timetable_id)
        )
        timetables = result.scalars().all()
        timetable_ids = [t.id for t in timetables if t.academic_year == academic_year and t.semester == semester]
        if timetable_ids:
            conditions.append(TeachingEvaluation.timetable_id.in_(timetable_ids))

    evaluations_result = await db.execute(
        select(TeachingEvaluation).where(and_(*conditions))
    )
    evaluations = evaluations_result.scalars().all()

    if not evaluations:
        return {
            "teacher_id": teacher_id,
            "teacher_name": teacher.user_name,
            "college_id": teacher.college_id,
            "college_name": None,
            "total_evaluation_num": 0,
            "avg_total_score": None,
            "max_score": None,
            "min_score": None,
            "dimension_avg_scores": None,
            "school_rank": None,
            "college_rank": None
        }

    scores = [e.total_score for e in evaluations]
    score_distribution = {
        "优秀": len([s for s in scores if s >= 90]),
        "良好": len([s for s in scores if 75 <= s < 90]),
        "合格": len([s for s in scores if 60 <= s < 75]),
        "不合格": len([s for s in scores if s < 60])
    }

    dimension_scores_list = [e.dimension_scores for e in evaluations if e.dimension_scores]
    dimension_avg_scores = {}
    if dimension_scores_list:
        all_dimensions = set()
        for ds in dimension_scores_list:
            all_dimensions.update(ds.keys())
        for dimension in all_dimensions:
            dim_scores = [ds.get(dimension, 0) for ds in dimension_scores_list]
            dimension_avg_scores[dimension] = round(mean(dim_scores), 2) if dim_scores else 0

    problems = [e.problem_content for e in evaluations if e.problem_content]
    suggestions = [e.improve_suggestion for e in evaluations if e.improve_suggestion]

    college = None
    if teacher.college_id:
        college_result = await db.execute(
            select(College).where(College.id == teacher.college_id)
        )
        college = college_result.scalar_one_or_none()

    return {
        "teacher_id": teacher_id,
        "teacher_name": teacher.user_name,
        "college_id": teacher.college_id,
        "college_name": college.college_name if college else None,
        "total_evaluation_num": len(evaluations),
        "avg_total_score": round(mean(scores), 2) if scores else None,
        "max_score": max(scores) if scores else None,
        "min_score": min(scores) if scores else None,
        "dimension_avg_scores": dimension_avg_scores,
        "score_distribution": score_distribution,
        "high_freq_problems": problems[:5] if problems else None,
        "high_freq_suggestions": suggestions[:5] if suggestions else None
    }


async def get_college_statistics(
    db: AsyncSession,
    college_id: int,
    academic_year: Optional[str] = None,
    semester: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """获取学院评教统计数据"""
    result = await db.execute(
        select(College).where(College.id == college_id)
    )
    college = result.scalar_one_or_none()
    if not college:
        return None

    teachers_result = await db.execute(
        select(User.id).where(
            User.college_id == college_id,
            User.status == 1,
            User.is_delete == False
        )
    )
    teacher_ids = [t[0] for t in teachers_result.all()]

    if not teacher_ids:
        return {
            "college_id": college_id,
            "college_name": college.college_name,
            "total_teacher_num": 0,
            "total_evaluation_num": 0,
            "avg_total_score": None,
            "dimension_avg_scores": None,
            "school_rank": None,
            "excellent_rate": None,
            "score_distribution": None,
            "high_freq_problems": None
        }

    conditions = [
        TeachingEvaluation.teach_teacher_id.in_(teacher_ids),
        TeachingEvaluation.is_delete == False,
        TeachingEvaluation.status == 1
    ]

    if academic_year and semester:
        result = await db.execute(
            select(Timetable.id).where(
                Timetable.academic_year == academic_year,
                Timetable.semester == semester
            )
        )
        timetable_ids = [t[0] for t in result.all()]
        if timetable_ids:
            conditions.append(TeachingEvaluation.timetable_id.in_(timetable_ids))

    evaluations_result = await db.execute(
        select(TeachingEvaluation).where(and_(*conditions))
    )
    evaluations = evaluations_result.scalars().all()

    scores = [e.total_score for e in evaluations] if evaluations else []
    score_distribution = {
        "优秀": len([s for s in scores if s >= 90]) if scores else 0,
        "良好": len([s for s in scores if 75 <= s < 90]) if scores else 0,
        "合格": len([s for s in scores if 60 <= s < 75]) if scores else 0,
        "不合格": len([s for s in scores if s < 60]) if scores else 0
    }

    excellent_count = score_distribution.get("优秀", 0)
    total_count = len(scores)
    excellent_rate = round(excellent_count / total_count * 100, 2) if total_count > 0 else None

    dimension_scores_list = [e.dimension_scores for e in evaluations if e.dimension_scores]
    dimension_avg_scores = {}
    if dimension_scores_list:
        all_dimensions = set()
        for ds in dimension_scores_list:
            all_dimensions.update(ds.keys())
        for dimension in all_dimensions:
            dim_scores = [ds.get(dimension, 0) for ds in dimension_scores_list]
            dimension_avg_scores[dimension] = round(mean(dim_scores), 2) if dim_scores else 0

    problems = []
    for e in evaluations:
        if e.problem_content:
            problems.append(e.problem_content)

    return {
        "college_id": college_id,
        "college_name": college.college_name,
        "total_teacher_num": len(teacher_ids),
        "total_evaluation_num": len(evaluations),
        "avg_total_score": round(mean(scores), 2) if scores else None,
        "dimension_avg_scores": dimension_avg_scores,
        "score_distribution": score_distribution,
        "excellent_rate": excellent_rate,
        "high_freq_problems": problems[:5] if problems else None
    }


async def get_school_statistics(
    db: AsyncSession,
    academic_year: Optional[str] = None,
    semester: Optional[int] = None
) -> Dict[str, Any]:
    """获取全校评教统计数据"""
    colleges_result = await db.execute(
        select(College.id, College.college_name).where(
            College.is_delete == False
        )
    )
    colleges = colleges_result.all()

    all_scores = []
    all_evaluations = []
    dimension_scores_list = []
    score_distribution = {"优秀": 0, "良好": 0, "合格": 0, "不合格": 0}
    college_stats = []

    for college_id, college_name in colleges:
        college_stat = await get_college_statistics(db, college_id, academic_year, semester)
        if college_stat and college_stat.get("total_evaluation_num", 0) > 0:
            college_stats.append({
                "college_id": college_id,
                "college_name": college_name,
                "total_evaluation_num": college_stat["total_evaluation_num"],
                "avg_total_score": college_stat["avg_total_score"]
            })
            if college_stat.get("avg_total_score"):
                all_scores.append(college_stat["avg_total_score"])

        if college_stat and college_stat.get("total_evaluation_num", 0) > 0:
            if college_stat.get("score_distribution"):
                for level, count in college_stat["score_distribution"].items():
                    score_distribution[level] += count
            if college_stat.get("dimension_avg_scores"):
                dimension_scores_list.append(college_stat["dimension_avg_scores"])

    evaluations_result = await db.execute(
        select(TeachingEvaluation).where(
            TeachingEvaluation.is_delete == False,
            TeachingEvaluation.status == 1
        )
    )
    all_evaluations = evaluations_result.scalars().all()

    if all_evaluations:
        scores = [e.total_score for e in all_evaluations]
        score_distribution = {
            "优秀": len([s for s in scores if s >= 90]),
            "良好": len([s for s in scores if 75 <= s < 90]),
            "合格": len([s for s in scores if 60 <= s < 75]),
            "不合格": len([s for s in scores if s < 60])
        }

    dimension_avg_scores = {}
    if dimension_scores_list:
        all_dimensions = set()
        for ds in dimension_scores_list:
            all_dimensions.update(ds.keys())
        for dimension in all_dimensions:
            dim_scores = [ds.get(dimension, 0) for ds in dimension_scores_list]
            dimension_avg_scores[dimension] = round(mean(dim_scores), 2) if dim_scores else 0

    college_stats_sorted = sorted(college_stats, key=lambda x: x.get("avg_total_score", 0) or 0, reverse=True)
    for i, stat in enumerate(college_stats_sorted):
        stat["rank"] = i + 1

    total_count = sum(score_distribution.values())
    excellent_rate = round(score_distribution["优秀"] / total_count * 100, 2) if total_count > 0 else None

    teachers_result = await db.execute(
        select(func.count(User.id)).where(
            User.status == 1,
            User.is_delete == False
        )
    )
    total_teacher_num = teachers_result.scalar() or 0

    return {
        "total_college_num": len(colleges),
        "total_teacher_num": total_teacher_num,
        "total_evaluation_num": len(all_evaluations),
        "avg_total_score": round(mean(all_scores), 2) if all_scores else None,
        "dimension_avg_scores": dimension_avg_scores,
        "excellent_rate": excellent_rate,
        "score_distribution": score_distribution,
        "college_rankings": college_stats_sorted
    }


async def update_evaluation_status_crud(
    db: AsyncSession,
    evaluation_id: int,
    status: int,
    review_comment: Optional[str] = None
) -> Optional[TeachingEvaluation]:
    """更新评教记录状态（审核）"""
    evaluation = await get_evaluation_by_id(db, evaluation_id)
    if not evaluation:
        return None

    evaluation.status = status
    if review_comment:
        evaluation.review_comment = review_comment

    try:
        await db.commit()
        await db.refresh(evaluation)
        return evaluation
    except Exception as e:
        await db.rollback()
        print(f"更新评教状态失败: {e}")
        return None
