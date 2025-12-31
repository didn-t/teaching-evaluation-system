# app/api/v1/teaching_eval/eval.py
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    BaseResponse,
    TokenData,
    EvaluationSubmit,
    EvaluationReviewRequest,
    CourseTypeUpdate,
)
from app.core.deps import get_current_user, require_access
from app.crud.evaluation import evaluation_crud
from app.crud.timetable import timetable_crud

# 如果你暂时还没把 college/school 统计迁移到 evaluation_crud，
# 可以先继续沿用旧函数（有的话就打开下面 import）
# from app.crud.evaluation import get_college_statistics, get_school_statistics

router = APIRouter(prefix="", tags=["评教管理"])


# -----------------------------
# 工具：把模型对象序列化成 dict
# -----------------------------
def _iso(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


def _timetable_brief(tt) -> dict:
    if not tt:
        return {}
    # 适配你 models 里的 Timetable 字段（没有 teach_time/teach_place）
    return {
        "id": tt.id,
        "academic_year": getattr(tt, "academic_year", None),
        "semester": getattr(tt, "semester", None),
        "course_name": getattr(tt, "course_name", None),
        "course_type": getattr(tt, "course_type", None),
        "class_name": getattr(tt, "class_name", None),
        "weekday": getattr(tt, "weekday", None),
        "weekday_text": getattr(tt, "weekday_text", None),
        "period": getattr(tt, "period", None),
        "section_time": getattr(tt, "section_time", None),
        "week_info": getattr(tt, "week_info", None),
        "classroom": getattr(tt, "classroom", None),
    }


# -----------------------------
# 1) 提交评教
# -----------------------------
@router.post(
    "/submit",
    summary="提交评教",
    response_model=BaseResponse,
)
async def submit_evaluation(
    submit_data: EvaluationSubmit,
    current_user: TokenData = Depends(
        require_access(roles_any=("teacher",), perms_all=("evaluation:submit",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    提交听课评教记录
    - 同一听课教师对同一课表同一天只能评教一次
    - 不能对自己教授课程评教
    """
    try:
        ev = await evaluation_crud.submit(
            db,
            timetable_id=submit_data.timetable_id,
            listen_teacher_id=current_user.id,
            total_score=submit_data.total_score,
            dimension_scores=submit_data.dimension_scores,
            listen_date=submit_data.listen_date,
            advantage_content=submit_data.advantage_content,
            problem_content=submit_data.problem_content,
            improve_suggestion=submit_data.improve_suggestion,
            listen_duration=submit_data.listen_duration,
            listen_location=submit_data.listen_location,
            is_anonymous=submit_data.is_anonymous,
            status=1,  # 默认有效/通过（你也可以改为 2=待审核）
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交评教失败: {e}")

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "id": ev.id,
            "evaluation_no": ev.evaluation_no,
            "total_score": ev.total_score,
            "score_level": ev.score_level,
            "submit_time": _iso(ev.submit_time),
        },
    )


# -----------------------------
# 2) 我提交的评教（新增，推荐用这个）
# -----------------------------
@router.get(
    "/mine",
    summary="我提交的评教列表",
    response_model=BaseResponse,
)
async def list_my_evaluations(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    status: Optional[int] = Query(
        None,
        description="状态：0作废/1有效/2待审核/3驳回",
    ),
    current_user: TokenData = Depends(
        require_access(roles_any=("teacher","supervisor","college_admin"))
    ),
    db: AsyncSession = Depends(get_db),
):
    items, total = await evaluation_crud.list_mine(
        db,
        listen_teacher_id=current_user.id,
        page=page,
        page_size=page_size,
        start_date=start_date,
        end_date=end_date,
        status=status,
    )

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "list": [
                {
                    "id": x.id,
                    "evaluation_no": x.evaluation_no,
                    "timetable_id": x.timetable_id,
                    "teach_teacher_id": x.teach_teacher_id,
                    "total_score": x.total_score,
                    "score_level": x.score_level,
                    "is_anonymous": x.is_anonymous,
                    "listen_date": _iso(x.listen_date),
                    "submit_time": _iso(x.submit_time),
                    "status": x.status,
                }
                for x in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


# 兼容旧接口：/list 等价于 /mine（你也可以删掉）
@router.get(
    "/list",
    summary="获取评教记录列表（兼容旧接口=mine）",
    response_model=BaseResponse,
)
async def get_evaluation_list_compat(
    page: int = 1,
    page_size: int = 10,
    current_user: TokenData = Depends(
        require_access(roles_any=("teacher","supervisor","college_admin"))
    ),
    db: AsyncSession = Depends(get_db),
):
    items, total = await evaluation_crud.list_mine(
        db,
        listen_teacher_id=current_user.id,
        page=page,
        page_size=page_size,
    )
    return BaseResponse(
        code=200,
        msg="success",
        data={
            "list": [
                {
                    "id": x.id,
                    "evaluation_no": x.evaluation_no,
                    "timetable_id": x.timetable_id,
                    "teach_teacher_id": x.teach_teacher_id,
                    "total_score": x.total_score,
                    "score_level": x.score_level,
                    "is_anonymous": x.is_anonymous,
                    "listen_date": _iso(x.listen_date),
                    "submit_time": _iso(x.submit_time),
                    "status": x.status,
                }
                for x in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


# -----------------------------
# 3) 评教详情：仅本人可看（需要的话可以再加“授课老师可看”接口）
# -----------------------------
@router.get(
    "/detail/{evaluation_id}",
    summary="获取评教详情（仅本人）",
    response_model=BaseResponse,
)
async def get_evaluation_detail(
    evaluation_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("teacher",), perms_all=("evaluation:read:self",))
    ),
    db: AsyncSession = Depends(get_db),
):
    ev = await evaluation_crud.get_by_id(db, evaluation_id=evaluation_id)
    if not ev:
        raise HTTPException(status_code=404, detail="评教记录不存在")

    if ev.listen_teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此评教记录")

    tt = await evaluation_crud.get_timetable(db, timetable_id=ev.timetable_id)

    return BaseResponse(
            code=200,
            msg="success",
            data={
                "id": ev.id,
                "evaluation_no": ev.evaluation_no,
                "timetable": _timetable_brief(tt),
                "teach_teacher_id": ev.teach_teacher_id,
                "teach_teacher_name": getattr(ev.teach_teacher, "user_name", None) if ev.teach_teacher else None,
                "listen_teacher_id": ev.listen_teacher_id,
                "listen_teacher_name": getattr(ev.listen_teacher, "user_name", None) if ev.listen_teacher else None,
                "total_score": ev.total_score,
                "dimension_scores": ev.dimension_scores,
                "score_level": ev.score_level,
                "advantage_content": ev.advantage_content,
                "problem_content": ev.problem_content,
                "improve_suggestion": ev.improve_suggestion,
                "listen_date": _iso(ev.listen_date),
                "listen_duration": ev.listen_duration,
                "listen_location": ev.listen_location,
                "is_anonymous": ev.is_anonymous,
                "status": ev.status,
                "submit_time": _iso(ev.submit_time),
                "create_time": _iso(getattr(ev, "create_time", None)),
            },
        )


# -----------------------------
# 4) 删除：仅本人（软删除）
# -----------------------------
@router.delete(
    "/{evaluation_id}",
    summary="删除评教记录（软删除）",
    response_model=BaseResponse,
)
async def delete_evaluation(
    evaluation_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("teacher",), perms_all=("evaluation:delete:self",))
    ),
    db: AsyncSession = Depends(get_db),
):
    ev = await evaluation_crud.get_by_id(db, evaluation_id=evaluation_id)
    if not ev:
        raise HTTPException(status_code=404, detail="评教记录不存在")

    if ev.listen_teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此评教记录")

    ok = await evaluation_crud.soft_delete(db, evaluation_id=evaluation_id)
    if not ok:
        raise HTTPException(status_code=500, detail="删除失败")

    return BaseResponse(code=200, msg="success", data=None)


# -----------------------------
# 5) 我收到的评教（新增，老师看自己被评教）
# -----------------------------
@router.get(
    "/received",
    summary="我收到的评教列表（授课老师视角）",
    response_model=BaseResponse,
)
async def list_received_evaluations(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    score_level: Optional[str] = Query(None, description="评分等级"),
    status: Optional[int] = Query(None, description="状态：0作废/1有效/2待审核/3驳回"),
    academic_year: Optional[str] = Query(None, description="学年（如2024-2025）"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="学期 1-春季 2-秋季"),
    current_user: TokenData = Depends(
        require_access(roles_any=("teacher",), perms_all=("evaluation:read:received",))
    ),
    db: AsyncSession = Depends(get_db),
):
    items, total = await evaluation_crud.list_by_teacher(
        db,
        teach_teacher_id=current_user.id,
        page=page,
        page_size=page_size,
        start_date=start_date,
        end_date=end_date,
        score_level=score_level,
        status=status,
        academic_year=academic_year,
        semester=semester,
    )

    data_list = []
    for ev in items:
        tt = getattr(ev, "timetable", None)
        listen_teacher = getattr(ev, "listen_teacher", None) if (not ev.is_anonymous) else None
        data_list.append(
            {
                "id": ev.id,
                "evaluation_no": ev.evaluation_no,
                "timetable": _timetable_brief(tt),
                "total_score": ev.total_score,
                "score_level": ev.score_level,
                "dimension_scores": ev.dimension_scores,
                "advantage_content": ev.advantage_content,
                "problem_content": ev.problem_content,
                "improve_suggestion": ev.improve_suggestion,
                "listen_date": _iso(ev.listen_date),
                "submit_time": _iso(ev.submit_time),
                "is_anonymous": ev.is_anonymous,
                "listen_teacher_id": ev.listen_teacher_id if not ev.is_anonymous else None,
                "listen_teacher_name": getattr(listen_teacher, "user_name", None) if listen_teacher else None,
                "status": ev.status,
            }
        )

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "list": data_list,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


# -----------------------------
# 6) 按课表查询评教记录（管理员/教务视角常用）
# -----------------------------
@router.get(
    "/timetable/{timetable_id}",
    summary="按课表查询评教记录",
    response_model=BaseResponse,
)
async def fetch_evaluations_by_timetable(
    timetable_id: int,
    current_user: TokenData = Depends(
        require_access(
            roles_any=("college_admin", "school_admin"),
            perms_all=("evaluation:read:received",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    tt = await evaluation_crud.get_timetable(db, timetable_id=timetable_id)
    if not tt:
        raise HTTPException(status_code=404, detail="课表不存在")

    evaluations = await evaluation_crud.list_by_timetable(db, timetable_id=timetable_id)

    result_list = []
    for ev in evaluations:
        listen_teacher = getattr(ev, "listen_teacher", None) if (not ev.is_anonymous) else None
        result_list.append(
            {
                "id": ev.id,
                "evaluation_no": ev.evaluation_no,
                "total_score": ev.total_score,
                "score_level": ev.score_level,
                "dimension_scores": ev.dimension_scores,
                "advantage_content": ev.advantage_content,
                "problem_content": ev.problem_content,
                "improve_suggestion": ev.improve_suggestion,
                "listen_date": _iso(ev.listen_date),
                "submit_time": _iso(ev.submit_time),
                "is_anonymous": ev.is_anonymous,
                "listen_teacher_id": ev.listen_teacher_id if not ev.is_anonymous else None,
                "listen_teacher_name": getattr(listen_teacher, "user_name", None) if listen_teacher else None,
                "status": ev.status,
            }
        )

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "timetable": _timetable_brief(tt),
            "list": result_list,
            "total": len(result_list),
        },
    )


# -----------------------------
# 7) 评价维度配置
# -----------------------------
@router.get(
    "/dimensions",
    summary="获取评价维度配置",
    response_model=BaseResponse,
)
async def get_evaluation_dimensions(
    current_user: TokenData = Depends(
        require_access(
            roles_any=("teacher", "college_admin", "school_admin"),
            perms_all=("evaluation:dimension:read",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    dims = await evaluation_crud.get_dimensions(db)
    return BaseResponse(
        code=200,
        msg="success",
        data=[
            {
                "id": d.id,
                "dimension_code": d.dimension_code,
                "dimension_name": d.dimension_name,
                "max_score": d.max_score,
                "weight": float(d.weight) if d.weight else 1.0,
                "sort_order": d.sort_order,
                "description": d.description,
                "scoring_criteria": d.scoring_criteria,
                "is_required": d.is_required,
                "status": d.status,
            }
            for d in dims
        ],
    )


# -----------------------------
# 8) 教师统计：我自己的（新增，最清晰）
# -----------------------------
@router.get(
    "/statistics/teacher/me",
    summary="获取我的评教统计（新增）",
    response_model=BaseResponse,
)
async def fetch_my_teacher_statistics(
    academic_year: Optional[str] = Query(None, description="学年（如2024-2025）"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="学期 1-春季 2-秋季"),
    current_user: TokenData = Depends(
        require_access(roles_any=("teacher",), perms_all=("evaluation:stats:teacher",))
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        stat = await evaluation_crud.teacher_statistics(
            db,
            teacher_id=current_user.id,
            academic_year=academic_year,
            semester=semester,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return BaseResponse(code=200, msg="success", data=stat)


# -----------------------------
# 9) 教师统计：指定教师（管理员用）
# -----------------------------
@router.get(
    "/statistics/teacher/{teacher_id}",
    summary="获取指定教师评教统计（管理员）",
    response_model=BaseResponse,
)
async def fetch_teacher_statistics_admin(
    teacher_id: int,
    academic_year: Optional[str] = Query(None, description="学年（如2024-2025）"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="学期 1-春季 2-秋季"),
    current_user: TokenData = Depends(
        require_access(
            roles_any=("college_admin", "school_admin"),
            perms_all=("evaluation:stats:teacher",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        stat = await evaluation_crud.teacher_statistics(
            db,
            teacher_id=teacher_id,
            academic_year=academic_year,
            semester=semester,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return BaseResponse(code=200, msg="success", data=stat)


# -----------------------------
# 10) 审核评教（统一入口）
# -----------------------------
@router.put(
    "/{evaluation_id}/review",
    summary="审核评教记录（统一入口）",
    response_model=BaseResponse,
)
async def review_evaluation(
    evaluation_id: int,
    review_data: EvaluationReviewRequest,
    current_user: TokenData = Depends(
        require_access(
            roles_any=("college_admin", "school_admin"),
            perms_all=("evaluation:review",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        ev = await evaluation_crud.update_status(
            db,
            evaluation_id=evaluation_id,
            status=review_data.status,
            review_comment=getattr(review_data, "review_comment", None),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"审核失败: {e}")

    if not ev:
        raise HTTPException(status_code=404, detail="评教记录不存在")

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "id": ev.id,
            "status": ev.status,
            "review_comment": getattr(ev, "review_comment", None),
        },
    )


# -----------------------------
# 11) 学院/全校统计（已实现）
# -----------------------------
@router.get(
    "/statistics/college/{college_id}",
    summary="获取学院评教统计",
    response_model=BaseResponse,
)
async def fetch_college_statistics(
    college_id: int,
    academic_year: Optional[str] = Query(None, description="学年（如2024-2025）"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="学期 1-春季 2-秋季"),
    current_user: TokenData = Depends(
        require_access(
            roles_any=("college_admin", "school_admin"),
            perms_all=("evaluation:stats:college",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    from app.crud.stats import get_college_statistics
    
    try:
        stat = await get_college_statistics(db, college_id=college_id, academic_year=academic_year, semester=semester)
        return BaseResponse(code=200, msg="success", data=stat)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/statistics/school",
    summary="获取全校评教统计",
    response_model=BaseResponse,
)
async def fetch_school_statistics(
    academic_year: Optional[str] = Query(None, description="学年（如2024-2025）"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="学期 1-春季 2-秋季"),
    current_user: TokenData = Depends(
        require_access(
            roles_any=("school_admin",),
            perms_all=("evaluation:stats:school",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    from app.crud.stats import get_school_statistics
    
    stat = await get_school_statistics(db, academic_year=academic_year, semester=semester)
    return BaseResponse(code=200, msg="success", data=stat)


# -----------------------------
# 12) 教师排名接口
# -----------------------------
@router.get(
    "/statistics/teacher/ranking",
    summary="获取教师排名",
    response_model=BaseResponse,
)
async def fetch_teacher_ranking(
    college_id: Optional[int] = Query(None, description="学院ID，为空则查询全校"),
    academic_year: Optional[str] = Query(None, description="学年（如2024-2025）"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="学期 1-春季 2-秋季"),
    course_type: Optional[str] = Query(None, description="课程类型"),
    current_user: TokenData = Depends(
        require_access(
            roles_any=("college_admin", "school_admin"),
            perms_all=("evaluation:stats:teacher",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    from app.crud.stats import get_teacher_ranking
    
    ranking = await get_teacher_ranking(
        db, 
        college_id=college_id, 
        academic_year=academic_year, 
        semester=semester,
        course_type=course_type
    )
    return BaseResponse(code=200, msg="success", data={
        "ranking": ranking,
        "total": len(ranking)
    })


# -----------------------------
# 13) 数据导出接口
# -----------------------------
@router.get(
    "/export/college",
    summary="导出学院评教数据",
    response_model=BaseResponse,
)
async def export_college_evaluation(
    college_id: int,
    academic_year: Optional[str] = Query(None, description="学年（如2024-2025）"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="学期 1-春季 2-秋季"),
    current_user: TokenData = Depends(
        require_access(
            roles_any=("college_admin", "school_admin"),
            perms_all=("evaluation:export:college",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    from app.crud.stats import get_college_statistics
    from datetime import datetime
    
    try:
        stat = await get_college_statistics(db, college_id=college_id, academic_year=academic_year, semester=semester)
        # 这里可以添加导出逻辑，比如生成Excel文件
        # 暂时返回数据结构，实际项目中应返回文件下载链接或文件流
        return BaseResponse(code=200, msg="success", data={
            "export_data": stat,
            "export_type": "college",
            "export_time": datetime.utcnow().isoformat()
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/export/school",
    summary="导出全校评教数据",
    response_model=BaseResponse,
)
async def export_school_evaluation(
    academic_year: Optional[str] = Query(None, description="学年（如2024-2025）"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="学期 1-春季 2-秋季"),
    current_user: TokenData = Depends(
        require_access(
            roles_any=("school_admin",),
            perms_all=("evaluation:export:all",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    from app.crud.stats import get_school_statistics
    from datetime import datetime
    
    stat = await get_school_statistics(db, academic_year=academic_year, semester=semester)
    # 这里可以添加导出逻辑，比如生成Excel文件
    # 暂时返回数据结构，实际项目中应返回文件下载链接或文件流
    return BaseResponse(code=200, msg="success", data={
        "export_data": stat,
        "export_type": "school",
        "export_time": datetime.utcnow().isoformat()
    })


# -----------------------------  
# 14) 获取待评课程列表  
# -----------------------------  
@router.get(
    "/pending-courses",
    summary="获取待评课程列表",
    response_model=BaseResponse,
)
async def get_pending_courses(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    academic_year: Optional[str] = Query(None, description="学年（如2024-2025）"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="学期 1-春季 2-秋季"),
    current_user: TokenData = Depends(
        require_access(
            roles_any=("teacher", "college_admin", "school_admin"),
            perms_all=("timetable:view:self", "evaluation:submit"),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有待评课程，即course_type为"待评"的课程
    """
    skip = (page - 1) * page_size
    items, total = await timetable_crud.list_pending_evaluation(
        db,
        academic_year=academic_year,
        semester=semester,
        skip=skip,
        limit=page_size,
    )

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "list": [
                {
                    "id": item.id,
                    "academic_year": item.academic_year,
                    "semester": item.semester,
                    "course_name": item.course_name,
                    "course_type": item.course_type,
                    "class_name": item.class_name,
                    "teacher_id": item.teacher_id,
                    "weekday": item.weekday,
                    "weekday_text": item.weekday_text,
                    "period": item.period,
                    "section_time": item.section_time,
                    "week_info": item.week_info,
                    "classroom": item.classroom,
                }
                for item in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


# -----------------------------  
# 15) 获取已评课程列表  
# -----------------------------  
@router.get(
    "/completed-courses",
    summary="获取已评课程列表",
    response_model=BaseResponse,
)
async def get_completed_courses(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    academic_year: Optional[str] = Query(None, description="学年（如2024-2025）"),
    semester: Optional[int] = Query(None, ge=1, le=2, description="学期 1-春季 2-秋季"),
    current_user: TokenData = Depends(
        require_access(
            roles_any=("teacher", "college_admin", "school_admin"),
            perms_all=("timetable:view:self", "evaluation:submit"),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有已评课程，即course_type为"已评"的课程
    """
    skip = (page - 1) * page_size
    items, total = await timetable_crud.list_completed_evaluation(
        db,
        academic_year=academic_year,
        semester=semester,
        skip=skip,
        limit=page_size,
    )

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "list": [
                {
                    "id": item.id,
                    "academic_year": item.academic_year,
                    "semester": item.semester,
                    "course_name": item.course_name,
                    "course_type": item.course_type,
                    "class_name": item.class_name,
                    "teacher_id": item.teacher_id,
                    "weekday": item.weekday,
                    "weekday_text": item.weekday_text,
                    "period": item.period,
                    "section_time": item.section_time,
                    "week_info": item.week_info,
                    "classroom": item.classroom,
                }
                for item in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    )


# -----------------------------  
# 16) 更新课程评价状态  
# -----------------------------  
@router.put(
    "/courses/{timetable_id}/course-type",
    summary="更新课程评价状态",
    response_model=BaseResponse,
)
async def update_course_type(
    timetable_id: int,
    update_data: CourseTypeUpdate,
    request: Request,
    current_user: TokenData = Depends(
        require_access(
            roles_any=("college_admin", "school_admin", "teacher"),
            perms_all=("evaluation:update:course_type",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    更新课程的评价状态，学院管理员、学校管理员及课程教师本人可以操作
    """
    # 验证course_type值是否合法
    # 去除空格后再验证
    course_type = update_data.course_type or ""
    const_course_type = course_type.strip()
    # 处理中文"空"字的情况
    if const_course_type == "空":
        const_course_type = ""
    if const_course_type not in ["", "待评", "已评"]:
        raise HTTPException(status_code=400, detail="课程评价状态只能是'待评'或'已评'或空")
    # 使用处理后的course_type
    course_type = const_course_type
    
    # 获取课程信息，检查权限
    timetable = await timetable_crud.get(db, id=timetable_id)
    if not timetable:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    # 检查课程是否已删除
    if getattr(timetable, 'is_delete', False):
        raise HTTPException(status_code=404, detail="课程不存在")
    
    # 获取用户角色信息
    user_roles = getattr(request, "state", None).user_roles if hasattr(request, "state") else []
    # 非管理员角色只能修改自己的课程
    if not any(role in user_roles for role in ["college_admin", "school_admin"]) and timetable.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改此课程的评价状态")
    
    try:
        # 更新课程状态
        updated_course = await timetable_crud.update_course_type(
            db,
            timetable_id=timetable_id,
            course_type=course_type
        )
        
        if not updated_course:
            raise HTTPException(status_code=404, detail="课程不存在")
        
        return BaseResponse(
            code=200,
            msg="success",
            data={
                "id": updated_course.id,
                "course_name": updated_course.course_name,
                "course_type": updated_course.course_type,
                "class_name": updated_course.class_name,
                "teacher_id": updated_course.teacher_id
            },
        )
    except Exception as e:
        # 记录详细错误信息
        print(f"更新课程评价状态失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
