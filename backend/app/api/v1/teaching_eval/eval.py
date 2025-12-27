from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.schemas import (
    BaseResponse,
    TokenData,
    EvaluationSubmit,
    EvaluationSubmitResponse,
    TeachingEvaluationResponse
)
from app.crud.teaching_eval.evaluation import (
    create_evaluation,
    get_evaluation_by_id,
    get_timetable_by_id,
    check_duplicate_evaluation
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
