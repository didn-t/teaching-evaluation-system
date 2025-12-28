from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_
from datetime import datetime
from typing import Optional, List

from app.database import get_db
from app.schemas import (
    BaseResponse,
    TokenData,
    EvaluationSubmit,
    EvaluationSubmitResponse,
    TeachingEvaluationResponse,
    EvaluationDimensionResponse,
    EvaluationReviewRequest,
    TeacherEvaluationDetailResponse,
    TeacherStatisticsResponse,
    CollegeStatisticsResponse,
    SchoolStatisticsResponse
)
from app.crud.teaching_eval.evaluation import (
    create_evaluation,
    get_evaluation_by_id,
    get_timetable_by_id,
    check_duplicate_evaluation,
    get_evaluation_dimensions as get_dimension_list,
    get_evaluations_by_teacher as get_teacher_eval_list,
    get_evaluations_by_timetable as get_timetable_eval_list,
    get_teacher_statistics as get_teacher_stats,
    get_college_statistics as get_college_stats,
    get_school_statistics as get_school_stats,
    update_evaluation_status_crud
)
from app.core.deps import get_current_user

router = APIRouter(prefix="/evaluation", tags=["评教管理"])


def get_score_level(score: int) -> str:
    """根据总分计算等级"""
    if score >= 90:
        return "优秀"
    elif score >= 75:
        return "良好"
    elif score >= 60:
        return "合格"
    else:
        return "不合格"


@router.post("/submit", response_model=BaseResponse[EvaluationSubmitResponse], summary="提交评教")
async def submit_evaluation(
    submit_data: EvaluationSubmit,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    提交听课评教记录

    - 需要登录认证
    - 同一听课教师对同一课表同一天只能评教一次
    """
    timetable = await get_timetable_by_id(db, submit_data.timetable_id)
    if not timetable:
        raise HTTPException(status_code=404, detail="课表不存在")

    if timetable.teacher_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能对自己教授的课程进行评教")

    is_duplicate = await check_duplicate_evaluation(
        db,
        submit_data.timetable_id,
        current_user.id,
        submit_data.listen_date
    )
    if is_duplicate:
        raise HTTPException(status_code=400, detail="该课表今日已由您评教，请勿重复提交")

    evaluation_no = f"EVAL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hash(current_user.id) % 100000:05d}"
    score_level = get_score_level(submit_data.total_score)

    from app.models import TeachingEvaluation
    evaluation = TeachingEvaluation(
        evaluation_no=evaluation_no,
        timetable_id=submit_data.timetable_id,
        teach_teacher_id=timetable.teacher_id,
        listen_teacher_id=current_user.id,
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

    db.add(evaluation)
    try:
        await db.commit()
        await db.refresh(evaluation)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"提交评教失败: {str(e)}")

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "id": evaluation.id,
            "evaluation_no": evaluation.evaluation_no,
            "total_score": evaluation.total_score,
            "score_level": evaluation.score_level,
            "submit_time": evaluation.submit_time.isoformat() if evaluation.submit_time else None
        }
    )


@router.get("/list", response_model=BaseResponse, summary="获取评教记录列表")
async def get_evaluation_list(
    page: int = 1,
    page_size: int = 10,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的评教记录列表

    - 需要登录认证
    - 支持分页查询
    """
    from app.models import TeachingEvaluation

    skip = (page - 1) * page_size

    result = await db.execute(
        select(TeachingEvaluation)
        .where(
            TeachingEvaluation.listen_teacher_id == current_user.id,
            TeachingEvaluation.is_delete == False
        )
        .order_by(TeachingEvaluation.submit_time.desc())
        .offset(skip)
        .limit(page_size)
    )
    evaluations = result.scalars().all()

    count_result = await db.execute(
        select(TeachingEvaluation.id)
        .where(
            TeachingEvaluation.listen_teacher_id == current_user.id,
            TeachingEvaluation.is_delete == False
        )
    )
    total = len(count_result.all())

    evaluation_list = []
    for eval_item in evaluations:
        evaluation_list.append({
            "id": eval_item.id,
            "evaluation_no": eval_item.evaluation_no,
            "timetable_id": eval_item.timetable_id,
            "teach_teacher_id": eval_item.teach_teacher_id,
            "total_score": eval_item.total_score,
            "score_level": eval_item.score_level,
            "is_anonymous": eval_item.is_anonymous,
            "listen_date": eval_item.listen_date.isoformat() if eval_item.listen_date else None,
            "submit_time": eval_item.submit_time.isoformat() if eval_item.submit_time else None,
            "status": eval_item.status
        })

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "list": evaluation_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/detail/{evaluation_id}", response_model=BaseResponse, summary="获取评教详情")
async def get_evaluation_detail(
    evaluation_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取评教记录详情

    - 需要登录认证
    - 只能查看自己创建的评教记录
    """
    evaluation = await get_evaluation_by_id(db, evaluation_id)

    if not evaluation:
        raise HTTPException(status_code=404, detail="评教记录不存在")

    if evaluation.listen_teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此评教记录")

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "id": evaluation.id,
            "evaluation_no": evaluation.evaluation_no,
            "timetable_id": evaluation.timetable_id,
            "teach_teacher_id": evaluation.teach_teacher_id,
            "listen_teacher_id": evaluation.listen_teacher_id,
            "total_score": evaluation.total_score,
            "dimension_scores": evaluation.dimension_scores,
            "score_level": evaluation.score_level,
            "advantage_content": evaluation.advantage_content,
            "problem_content": evaluation.problem_content,
            "improve_suggestion": evaluation.improve_suggestion,
            "listen_date": evaluation.listen_date.isoformat() if evaluation.listen_date else None,
            "listen_duration": evaluation.listen_duration,
            "listen_location": evaluation.listen_location,
            "is_anonymous": evaluation.is_anonymous,
            "status": evaluation.status,
            "submit_time": evaluation.submit_time.isoformat() if evaluation.submit_time else None,
            "create_time": evaluation.create_time.isoformat() if evaluation.create_time else None
        }
    )


@router.delete("/{evaluation_id}", response_model=BaseResponse, summary="删除评教记录")
async def delete_evaluation(
    evaluation_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除评教记录（软删除）

    - 需要登录认证
    - 只能删除自己创建的评教记录
    """
    evaluation = await get_evaluation_by_id(db, evaluation_id)

    if not evaluation:
        raise HTTPException(status_code=404, detail="评教记录不存在")

    if evaluation.listen_teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此评教记录")

    evaluation.is_delete = True
    await db.commit()
    await db.refresh(evaluation)

    return BaseResponse(
        code=200,
        msg="success",
        data=None
    )


@router.put("/{evaluation_id}/status", response_model=BaseResponse, summary="更新评教状态")
async def update_evaluation_status(
    evaluation_id: int,
    status: int = Query(..., ge=1, le=3, description="状态: 1-待审核 2-已通过 3-已驳回"),
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新评教记录状态

    - 需要登录认证
    - status: 1-待审核, 2-已通过, 3-已驳回
    """
    evaluation = await get_evaluation_by_id(db, evaluation_id)

    if not evaluation:
        raise HTTPException(status_code=404, detail="评教记录不存在")

    evaluation.status = status
    await db.commit()
    await db.refresh(evaluation)

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "id": evaluation.id,
            "status": evaluation.status
        }
    )


@router.get("/dimensions", response_model=BaseResponse, summary="获取评价维度配置")
async def get_evaluation_dimensions(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有启用的评价维度配置

    - 需要登录认证
    - 返回评教的各个维度及最高分、权重等信息
    """
    dimensions = await get_dimension_list(db)

    dimension_list = []
    for dim in dimensions:
        dimension_list.append({
            "id": dim.id,
            "dimension_code": dim.dimension_code,
            "dimension_name": dim.dimension_name,
            "max_score": dim.max_score,
            "weight": float(dim.weight) if dim.weight else 1.0,
            "sort_order": dim.sort_order,
            "description": dim.description,
            "scoring_criteria": dim.scoring_criteria,
            "is_required": dim.is_required,
            "status": dim.status
        })

    return BaseResponse(
        code=200,
        msg="success",
        data=dimension_list
    )


@router.get("/statistics/teacher/{teacher_id}", response_model=BaseResponse, summary="获取教师评教统计")
async def fetch_teacher_statistics(
    teacher_id: int,
    academic_year: Optional[str] = Query(None, description="学年（如2024-2025）"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="学期 1-春季 2-秋季"),
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定教师的评教统计数据

    - 需要登录认证
    - 支持按学年、学期筛选
    """
    from app.models import User

    result = await db.execute(
        select(User).where(User.id == teacher_id)
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="教师不存在")

    stat = await get_teacher_stats(db, teacher_id, academic_year, semester)

    return BaseResponse(
        code=200,
        msg="success",
        data=stat
    )


@router.get("/statistics/college/{college_id}", response_model=BaseResponse, summary="获取学院评教统计")
async def fetch_college_statistics(
    college_id: int,
    academic_year: Optional[str] = Query(None, description="学年（如2024-2025）"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="学期 1-春季 2-秋季"),
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定学院的评教统计数据

    - 需要登录认证（学院管理员/学校管理员）
    - 支持按学年、学期筛选
    """
    from app.models import College

    result = await db.execute(
        select(College).where(College.id == college_id)
    )
    college = result.scalar_one_or_none()
    if not college:
        raise HTTPException(status_code=404, detail="学院不存在")

    stat = await get_college_stats(db, college_id, academic_year, semester)

    return BaseResponse(
        code=200,
        msg="success",
        data=stat
    )


@router.get("/statistics/school", response_model=BaseResponse, summary="获取全校评教统计")
async def fetch_school_statistics(
    academic_year: Optional[str] = Query(None, description="学年（如2024-2025）"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="学期 1-春季 2-秋季"),
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取全校评教统计数据

    - 需要登录认证（学校管理员）
    - 支持按学年、学期筛选
    """
    stat = await get_school_stats(db, academic_year, semester)

    return BaseResponse(
        code=200,
        msg="success",
        data=stat
    )


@router.get("/teacher/{teacher_id}", response_model=BaseResponse, summary="获取教师评教记录")
async def get_teacher_evaluations(
    teacher_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    score_level: Optional[str] = Query(None, description="评分等级"),
    status: Optional[int] = Query(None, description="状态"),
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定教师的所有评教记录

    - 需要登录认证
    - 支持分页和条件筛选
    """
    from app.models import User, Timetable

    result = await db.execute(
        select(User).where(User.id == teacher_id)
    )
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="教师不存在")

    evaluations, total = await get_teacher_eval_list(
        db, teacher_id, page, page_size, start_date, end_date, score_level, status
    )

    evaluation_list = []
    for eval_item in evaluations:
        timetable_result = await db.execute(
            select(Timetable).where(Timetable.id == eval_item.timetable_id)
        )
        timetable = timetable_result.scalar_one_or_none()

        listen_teacher = None
        if not eval_item.is_anonymous:
            listen_result = await db.execute(
                select(User).where(User.id == eval_item.listen_teacher_id)
            )
            listen_teacher = listen_result.scalar_one_or_none()

        evaluation_list.append({
            "id": eval_item.id,
            "evaluation_no": eval_item.evaluation_no,
            "timetable_id": eval_item.timetable_id,
            "course_name": timetable.course_name if timetable else None,
            "course_type": timetable.course_type if timetable else None,
            "class_name": timetable.class_name if timetable else None,
            "teach_teacher_id": eval_item.teach_teacher_id,
            "teach_teacher_name": teacher.user_name,
            "total_score": eval_item.total_score,
            "dimension_scores": eval_item.dimension_scores,
            "score_level": eval_item.score_level,
            "advantage_content": eval_item.advantage_content,
            "problem_content": eval_item.problem_content,
            "improve_suggestion": eval_item.improve_suggestion,
            "listen_date": eval_item.listen_date.isoformat() if eval_item.listen_date else None,
            "listen_duration": eval_item.listen_duration,
            "listen_location": eval_item.listen_location,
            "is_anonymous": eval_item.is_anonymous,
            "status": eval_item.status,
            "submit_time": eval_item.submit_time.isoformat() if eval_item.submit_time else None,
            "listen_teacher_id": eval_item.listen_teacher_id if not eval_item.is_anonymous else None,
            "listen_teacher_name": listen_teacher.user_name if listen_teacher and not eval_item.is_anonymous else None
        })

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "list": evaluation_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/timetable/{timetable_id}", response_model=BaseResponse, summary="按课表查询评教记录")
async def fetch_evaluations_by_timetable(
    timetable_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取指定课表的所有评教记录

    - 需要登录认证
    """
    from app.models import User, Timetable

    timetable = await get_timetable_by_id(db, timetable_id)
    if not timetable:
        raise HTTPException(status_code=404, detail="课表不存在")

    evaluations = await get_timetable_eval_list(db, timetable_id)

    teach_result = await db.execute(
        select(User).where(User.id == timetable.teacher_id)
    )
    teach_teacher = teach_result.scalar_one_or_none()

    evaluation_list = []
    for eval_item in evaluations:
        listen_teacher = None
        if not eval_item.is_anonymous:
            listen_result = await db.execute(
                select(User).where(User.id == eval_item.listen_teacher_id)
            )
            listen_teacher = listen_result.scalar_one_or_none()

        evaluation_list.append({
            "id": eval_item.id,
            "evaluation_no": eval_item.evaluation_no,
            "timetable_id": eval_item.timetable_id,
            "course_name": timetable.course_name,
            "course_type": timetable.course_type,
            "class_name": timetable.class_name,
            "teach_teacher_id": eval_item.teach_teacher_id,
            "teach_teacher_name": teach_teacher.user_name if teach_teacher else None,
            "total_score": eval_item.total_score,
            "dimension_scores": eval_item.dimension_scores,
            "score_level": eval_item.score_level,
            "advantage_content": eval_item.advantage_content,
            "problem_content": eval_item.problem_content,
            "improve_suggestion": eval_item.improve_suggestion,
            "listen_date": eval_item.listen_date.isoformat() if eval_item.listen_date else None,
            "listen_duration": eval_item.listen_duration,
            "listen_location": eval_item.listen_location,
            "is_anonymous": eval_item.is_anonymous,
            "status": eval_item.status,
            "submit_time": eval_item.submit_time.isoformat() if eval_item.submit_time else None,
            "listen_teacher_id": eval_item.listen_teacher_id if not eval_item.is_anonymous else None,
            "listen_teacher_name": listen_teacher.user_name if listen_teacher and not eval_item.is_anonymous else None
        })

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "timetable": {
                "id": timetable.id,
                "course_name": timetable.course_name,
                "course_type": timetable.course_type,
                "class_name": timetable.class_name,
                "teach_time": timetable.teach_time,
                "teach_place": timetable.teach_place,
                "teacher_id": timetable.teacher_id,
                "teacher_name": teach_teacher.user_name if teach_teacher else None
            },
            "list": evaluation_list,
            "total": len(evaluation_list)
        }
    )


@router.put("/{evaluation_id}/review", response_model=BaseResponse, summary="审核评教记录")
async def review_evaluation(
    evaluation_id: int,
    review_data: EvaluationReviewRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    审核评教记录（设置状态）

    - 需要登录认证（管理员）
    - status: 0-作废 1-有效 2-待审核
    """
    evaluation = await update_evaluation_status_crud(
        db, evaluation_id, review_data.status, review_data.review_comment
    )

    if not evaluation:
        raise HTTPException(status_code=404, detail="评教记录不存在")

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "id": evaluation.id,
            "status": evaluation.status,
            "review_comment": evaluation.review_comment
        }
    )
