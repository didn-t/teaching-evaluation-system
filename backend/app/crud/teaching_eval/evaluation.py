import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound

from app.models import TeachingEvaluation, Timetable, User
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
