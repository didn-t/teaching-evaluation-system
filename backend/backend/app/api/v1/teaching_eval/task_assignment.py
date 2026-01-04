# 22300417陈俫坤开发：督导评教任务分配接口
from __future__ import annotations

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, Field

from app.database import get_db
from app.schemas import BaseResponse, TokenData
from app.core.deps import require_access
from app.models import Timetable, User, TeachingEvaluation
from app.crud.user import get_roles_code

router = APIRouter(prefix="", tags=["督导任务分配"])


class TaskAssignmentRequest(BaseModel):
    """督导任务分配请求"""
    supervisor_user_ids: List[int] = Field(..., description="督导用户ID列表")
    timetable_ids: List[int] = Field(..., description="课表ID列表")
    deadline: Optional[datetime] = Field(None, description="评教截止时间")
    note: Optional[str] = Field(None, max_length=500, description="任务说明")


@router.post("/assign-evaluation-tasks", summary="学院管理员分配督导评教任务")
async def assign_evaluation_tasks(
    request: TaskAssignmentRequest,
    current_user: TokenData = Depends(
        require_access(
            roles_any=("college_admin", "school_admin"),
            perms_all=("user:manage:college",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """22300417陈俫坤开发：学院管理员给督导分配评教任务
    
    功能：
    - 学院管理员可以指定督导老师对特定课程进行评教
    - 避免督导不知道应该评教哪些课程的问题
    - 支持批量分配和截止时间设置
    """
    
    # 权限检查：学院管理员只能分配本学院的任务
    roles = await get_roles_code(db, current_user)
    if "college_admin" in roles and "school_admin" not in roles:
        if not getattr(current_user, "college_id", None):
            raise HTTPException(status_code=403, detail="学院管理员未设置学院")
        
        # 检查课表是否都属于本学院
        stmt = select(Timetable.id).where(
            Timetable.id.in_(request.timetable_ids),
            Timetable.college_id != current_user.college_id,
            Timetable.is_delete == False
        )
        invalid_timetables = (await db.execute(stmt)).scalars().all()
        if invalid_timetables:
            raise HTTPException(status_code=403, detail=f"课表ID {list(invalid_timetables)} 不属于您的学院")
    
    # 验证督导用户存在且有督导角色
    from app.crud.user import get_roles_code as get_user_roles
    for supervisor_id in request.supervisor_user_ids:
        supervisor_roles = await get_user_roles(db, TokenData(id=supervisor_id, user_on="", college_id=None, status=1, is_delete=False))
        if "supervisor" not in supervisor_roles:
            raise HTTPException(status_code=400, detail=f"用户ID {supervisor_id} 不是督导角色")
    
    # 验证课表存在
    stmt = select(Timetable.id).where(
        Timetable.id.in_(request.timetable_ids),
        Timetable.is_delete == False
    )
    valid_timetables = list((await db.execute(stmt)).scalars().all())
    if len(valid_timetables) != len(request.timetable_ids):
        invalid_ids = set(request.timetable_ids) - set(valid_timetables)
        raise HTTPException(status_code=400, detail=f"课表ID {list(invalid_ids)} 不存在或已删除")
    
    # 创建任务分配记录（这里可以扩展为专门的任务表，暂时用评教表的特殊状态）
    assignments_created = 0
    for supervisor_id in request.supervisor_user_ids:
        for timetable_id in request.timetable_ids:
            # 检查是否已经分配过
            existing = await db.execute(
                select(TeachingEvaluation.id).where(
                    TeachingEvaluation.timetable_id == timetable_id,
                    TeachingEvaluation.listen_teacher_id == supervisor_id,
                    TeachingEvaluation.is_delete == False
                )
            )
            if existing.scalar_one_or_none():
                continue  # 已存在，跳过
            
            # 创建任务分配记录（status=2表示待评教任务）
            assignment = TeachingEvaluation(
                timetable_id=timetable_id,
                listen_teacher_id=supervisor_id,
                total_score=0,  # 占位值
                status=2,  # 2=待评教任务
                submit_time=datetime.utcnow(),
                is_delete=False,
                # 任务相关字段
                improve_suggestion=f"任务分配：{request.note or '请完成评教'}"
            )
            db.add(assignment)
            assignments_created += 1
    
    await db.commit()
    
    return BaseResponse(
        code=200,
        msg="success",
        data={
            "assignments_created": assignments_created,
            "supervisor_count": len(request.supervisor_user_ids),
            "timetable_count": len(request.timetable_ids),
            "deadline": request.deadline.isoformat() if request.deadline else None
        }
    )


@router.get("/supervisor-tasks", summary="获取督导评教任务列表")
async def get_supervisor_tasks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[int] = Query(None, description="任务状态：2=待评教，1=已完成"),
    current_user: TokenData = Depends(
        require_access(
            roles_any=("supervisor", "college_admin", "school_admin"),
            perms_all=("evaluation:view:college",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """22300417陈俫坤开发：获取督导评教任务列表
    
    - 督导查看自己的任务
    - 学院管理员查看本学院督导任务
    """
    
    skip = (page - 1) * page_size
    filters = []
    
    # 角色权限过滤
    roles = await get_roles_code(db, current_user)
    if "supervisor" in roles and "college_admin" not in roles and "school_admin" not in roles:
        # 督导只能看自己的任务
        filters.append(TeachingEvaluation.listen_teacher_id == current_user.id)
    elif "college_admin" in roles and "school_admin" not in roles:
        # 学院管理员看本学院督导任务
        if not getattr(current_user, "college_id", None):
            raise HTTPException(status_code=403, detail="学院管理员未设置学院")
        # 通过课表关联过滤学院
        filters.append(Timetable.college_id == current_user.college_id)
    
    if status is not None:
        filters.append(TeachingEvaluation.status == status)
    
    filters.extend([
        TeachingEvaluation.is_delete == False,
        Timetable.is_delete == False
    ])
    
    # 查询任务
    stmt = (
        select(TeachingEvaluation, Timetable, User)
        .join(Timetable, TeachingEvaluation.timetable_id == Timetable.id)
        .join(User, TeachingEvaluation.listen_teacher_id == User.id)
        .where(and_(*filters))
        .order_by(TeachingEvaluation.submit_time.desc())
        .offset(skip)
        .limit(page_size)
    )
    
    result = await db.execute(stmt)
    tasks = []
    
    for evaluation, timetable, supervisor in result.all():
        tasks.append({
            "id": evaluation.id,
            "timetable_id": timetable.id,
            "course_name": timetable.course_name,
            "class_name": timetable.class_name,
            "academic_year": timetable.academic_year,
            "semester": timetable.semester,
            "supervisor_id": supervisor.id,
            "supervisor_name": supervisor.user_name,
            "status": evaluation.status,
            "status_text": "待评教" if evaluation.status == 2 else "已完成",
            "assign_time": evaluation.submit_time.isoformat(),
            "note": evaluation.improve_suggestion
        })
    
    # 统计总数
    count_stmt = (
        select(TeachingEvaluation.id)
        .join(Timetable, TeachingEvaluation.timetable_id == Timetable.id)
        .where(and_(*filters))
    )
    total = len((await db.execute(count_stmt)).scalars().all())
    
    return BaseResponse(
        code=200,
        msg="success",
        data={
            "list": tasks,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )
