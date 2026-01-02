# app/api/v1/teaching_eval/org.py
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    BaseResponse,
    CollegeCreate,
    CollegeUpdate,
    CollegeResponse,
    ResearchRoomCreate,
    ResearchRoomUpdate,
    ResearchRoomResponse,
    MajorCreate,
    MajorUpdate,
    MajorResponse,
    ClazzCreate,
    ClazzUpdate,
    ClazzResponse,
    TimetableCreate,
    TimetableUpdate,
    TimetableResponse,
    TokenData,
)
from app.core.deps import get_current_user, require_access
from app.crud.user import get_roles_code
from app.crud.user import get_effective_supervisor_scope
from app.crud.org import (
    college_crud,
    research_room_crud,
    major_crud,
    clazz_crud,
)
from app.crud.timetable import timetable_crud

router = APIRouter(prefix="", tags=["组织结构管理"])


@router.get("/research-rooms", summary="获取教研室列表")
async def list_research_rooms(
    college_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 200,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin", "college_admin", "supervisor"), perms_all=("org:research_room:read",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """22300417陈俫坤开发：用于督导范围配置时拉取教研室列表"""
    filters = []
    if college_id:
        filters.append(research_room_crud.model.college_id == college_id)
    rooms, total = await research_room_crud.get_multi(db, skip=skip, limit=limit, filters=filters)
    return BaseResponse(code=200, msg="success", data={
        "list": [ResearchRoomResponse.model_validate(x) for x in rooms],
        "total": total,
        "skip": skip,
        "limit": limit,
    })


# -----------------------------
# 学院相关接口
# -----------------------------
@router.post("/college", summary="添加学院")
async def create_college(
    college_data: CollegeCreate,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("org:college:create",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """添加学院"""
    try:
        college = await college_crud.create(db, obj_in=college_data)
        return BaseResponse(code=200, msg="success", data=CollegeResponse.from_orm(college))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加学院失败: {e}")


@router.get("/college/{college_id}", summary="获取学院详情")
async def get_college(
    college_id: int,
    current_user: TokenData = Depends(
        # 22300417陈俫坤开发：督导老师需要查看负责学院信息
        require_access(roles_any=("school_admin", "college_admin", "supervisor", "teacher"), perms_all=("org:college:read",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取学院详情"""
    college = await college_crud.get(db, id=college_id)
    if not college:
        raise HTTPException(status_code=404, detail="学院不存在")
    return BaseResponse(code=200, msg="success", data=CollegeResponse.from_orm(college))


@router.put("/college/{college_id}", summary="更新学院信息")
async def update_college(
    college_id: int,
    college_data: CollegeUpdate,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("org:college:update",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """更新学院信息"""
    college = await college_crud.get(db, id=college_id)
    if not college:
        raise HTTPException(status_code=404, detail="学院不存在")
    
    try:
        updated_college = await college_crud.update(db, db_obj=college, obj_in=college_data, exclude_unset=True)
        return BaseResponse(code=200, msg="success", data=CollegeResponse.from_orm(updated_college))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新学院失败: {e}")


@router.delete("/college/{college_id}", summary="删除学院")
async def delete_college(
    college_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("org:college:delete",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """删除学院（软删除）"""
    college = await college_crud.get(db, id=college_id)
    if not college:
        raise HTTPException(status_code=404, detail="学院不存在")
    
    try:
        deleted_college = await college_crud.soft_remove(db, id=college_id)
        return BaseResponse(code=200, msg="success", data=CollegeResponse.from_orm(deleted_college))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除学院失败: {e}")


@router.get("/colleges", summary="获取学院列表")
async def list_colleges(
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(
        # 22300417陈俫坤开发：督导老师需要拉取学院列表用于范围筛选/统计
        require_access(roles_any=("school_admin", "college_admin", "supervisor", "teacher"), perms_all=("org:college:read",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取学院列表"""
    colleges, total = await college_crud.get_multi(db, skip=skip, limit=limit)
    # 转换为响应模型
    college_responses = [CollegeResponse.model_validate(college) for college in colleges]
    return BaseResponse(
        code=200,
        msg="success",
        data={
            "list": college_responses,
            "total": total,
            "skip": skip,
            "limit": limit,
        },
    )


# -----------------------------
# 教研室相关接口
# -----------------------------
@router.post("/research-room", summary="添加教研室")
async def create_research_room(
    research_room_data: ResearchRoomCreate,
    current_user: TokenData = Depends(
        require_access(roles_any=("college_admin", "school_admin"), perms_all=("org:research_room:create",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """添加教研室"""
    try:
        research_room = await research_room_crud.create(db, obj_in=research_room_data)
        return BaseResponse(code=200, msg="success", data=ResearchRoomResponse.model_validate(research_room))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加教研室失败: {e}")


@router.get("/research-room/{research_room_id}", summary="获取教研室详情")
async def get_research_room(
    research_room_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin", "college_admin", "teacher"), perms_all=("org:research_room:read",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取教研室详情"""
    research_room = await research_room_crud.get(db, id=research_room_id)
    if not research_room:
        raise HTTPException(status_code=404, detail="教研室不存在")
    return BaseResponse(code=200, msg="success", data=ResearchRoomResponse.model_validate(research_room))


@router.put("/research-room/{research_room_id}", summary="更新教研室信息")
async def update_research_room(
    research_room_id: int,
    research_room_data: ResearchRoomUpdate,
    current_user: TokenData = Depends(
        require_access(roles_any=("college_admin", "school_admin"), perms_all=("org:research_room:update",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """更新教研室信息"""
    research_room = await research_room_crud.get(db, id=research_room_id)
    if not research_room:
        raise HTTPException(status_code=404, detail="教研室不存在")
    
    try:
        updated_research_room = await research_room_crud.update(
            db, db_obj=research_room, obj_in=research_room_data, exclude_unset=True
        )
        return BaseResponse(code=200, msg="success", data=ResearchRoomResponse.model_validate(updated_research_room))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新教研室失败: {e}")


@router.delete("/research-room/{research_room_id}", summary="删除教研室")
async def delete_research_room(
    research_room_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("college_admin", "school_admin"), perms_all=("org:research_room:delete",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """删除教研室（软删除）"""
    research_room = await research_room_crud.get(db, id=research_room_id)
    if not research_room:
        raise HTTPException(status_code=404, detail="教研室不存在")
    
    try:
        deleted_research_room = await research_room_crud.soft_remove(db, id=research_room_id)
        return BaseResponse(code=200, msg="success", data=ResearchRoomResponse.model_validate(deleted_research_room))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除教研室失败: {e}")


# -----------------------------
# 专业相关接口
# -----------------------------
@router.post("/major", summary="添加专业")
async def create_major(
    major_data: MajorCreate,
    current_user: TokenData = Depends(
        require_access(roles_any=("college_admin", "school_admin"), perms_all=("org:major:create",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """添加专业"""
    try:
        major = await major_crud.create(db, obj_in=major_data)
        return BaseResponse(code=200, msg="success", data=MajorResponse.model_validate(major))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加专业失败: {e}")


@router.get("/major/{major_id}", summary="获取专业详情")
async def get_major(
    major_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin", "college_admin", "teacher"), perms_all=("org:major:read",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取专业详情"""
    major = await major_crud.get(db, id=major_id)
    if not major:
        raise HTTPException(status_code=404, detail="专业不存在")
    return BaseResponse(code=200, msg="success", data=MajorResponse.model_validate(major))


@router.put("/major/{major_id}", summary="更新专业信息")
async def update_major(
    major_id: int,
    major_data: MajorUpdate,
    current_user: TokenData = Depends(
        require_access(roles_any=("college_admin", "school_admin"), perms_all=("org:major:update",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """更新专业信息"""
    major = await major_crud.get(db, id=major_id)
    if not major:
        raise HTTPException(status_code=404, detail="专业不存在")
    
    try:
        updated_major = await major_crud.update(db, db_obj=major, obj_in=major_data, exclude_unset=True)
        return BaseResponse(code=200, msg="success", data=MajorResponse.model_validate(updated_major))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新专业失败: {e}")


@router.delete("/major/{major_id}", summary="删除专业")
async def delete_major(
    major_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("college_admin", "school_admin"), perms_all=("org:major:delete",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """删除专业（软删除）"""
    major = await major_crud.get(db, id=major_id)
    if not major:
        raise HTTPException(status_code=404, detail="专业不存在")
    
    try:
        deleted_major = await major_crud.soft_remove(db, id=major_id)
        return BaseResponse(code=200, msg="success", data=MajorResponse.model_validate(deleted_major))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除专业失败: {e}")


# -----------------------------
# 班级相关接口
# -----------------------------
@router.post("/clazz", summary="添加班级")
async def create_clazz(
    clazz_data: ClazzCreate,
    current_user: TokenData = Depends(
        require_access(roles_any=("college_admin", "school_admin"), perms_all=("org:clazz:create",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """添加班级"""
    try:
        clazz = await clazz_crud.create(db, obj_in=clazz_data)
        return BaseResponse(code=200, msg="success", data=ClazzResponse.model_validate(clazz))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加班级失败: {e}")


@router.get("/clazz/{clazz_id}", summary="获取班级详情")
async def get_clazz(
    clazz_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin", "college_admin", "teacher"), perms_all=("org:clazz:read",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取班级详情"""
    clazz = await clazz_crud.get(db, id=clazz_id)
    if not clazz:
        raise HTTPException(status_code=404, detail="班级不存在")
    return BaseResponse(code=200, msg="success", data=ClazzResponse.model_validate(clazz))


@router.put("/clazz/{clazz_id}", summary="更新班级信息")
async def update_clazz(
    clazz_id: int,
    clazz_data: ClazzUpdate,
    current_user: TokenData = Depends(
        require_access(roles_any=("college_admin", "school_admin"), perms_all=("org:clazz:update",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """更新班级信息"""
    clazz = await clazz_crud.get(db, id=clazz_id)
    if not clazz:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    try:
        updated_clazz = await clazz_crud.update(db, db_obj=clazz, obj_in=clazz_data, exclude_unset=True)
        return BaseResponse(code=200, msg="success", data=ClazzResponse.model_validate(updated_clazz))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新班级失败: {e}")


@router.delete("/clazz/{clazz_id}", summary="删除班级")
async def delete_clazz(
    clazz_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("college_admin", "school_admin"), perms_all=("org:clazz:delete",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """删除班级（软删除）"""
    clazz = await clazz_crud.get(db, id=clazz_id)
    if not clazz:
        raise HTTPException(status_code=404, detail="班级不存在")
    
    try:
        deleted_clazz = await clazz_crud.soft_remove(db, id=clazz_id)
        return BaseResponse(code=200, msg="success", data=ClazzResponse.model_validate(deleted_clazz))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除班级失败: {e}")


# -----------------------------
# 课表相关接口
# -----------------------------
@router.post("/timetable", summary="添加课表")
async def create_timetable(
    timetable_data: TimetableCreate,
    current_user: TokenData = Depends(
        require_access(roles_any=("college_admin", "school_admin"), perms_all=("org:timetable:create",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """添加课表（支持幂等操作）"""
    try:
        # 将TimetableCreate转换为字典格式用于upsert操作
        timetable_dict = timetable_data.model_dump()
        timetable = await timetable_crud.upsert(db, payload=timetable_dict)
        return BaseResponse(code=200, msg="success", data=TimetableResponse.model_validate(timetable))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加课表失败: {e}")


@router.get("/timetable/{timetable_id}", summary="获取课表详情")
async def get_timetable(
    timetable_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin", "college_admin", "teacher"))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取课表详情"""
    # 使用timetable_crud的get_multi方法来获取特定ID的课表
    timetables, total = await timetable_crud.get_multi(db, filters=[timetable_crud.model.id == timetable_id], limit=1)
    if not timetables:
        raise HTTPException(status_code=404, detail="课表不存在")
    return BaseResponse(code=200, msg="success", data=TimetableResponse.model_validate(timetables[0]))


@router.put("/timetable/{timetable_id}", summary="更新课表信息")
async def update_timetable(
    timetable_id: int,
    timetable_data: TimetableUpdate,
    current_user: TokenData = Depends(
        require_access(roles_any=("college_admin", "school_admin"), perms_all=("org:timetable:update",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """更新课表信息"""
    # 获取课表
    timetables, total = await timetable_crud.get_multi(db, filters=[timetable_crud.model.id == timetable_id], limit=1)
    if not timetables:
        raise HTTPException(status_code=404, detail="课表不存在")
    
    try:
        updated_timetable = await timetable_crud.update(
            db, db_obj=timetables[0], obj_in=timetable_data, exclude_unset=True
        )
        return BaseResponse(code=200, msg="success", data=TimetableResponse.model_validate(updated_timetable))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新课表失败: {e}")


@router.delete("/timetable/{timetable_id}", summary="删除课表")
async def delete_timetable(
    timetable_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("college_admin", "school_admin"), perms_all=("org:timetable:delete",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """删除课表（软删除）"""
    # 获取课表
    timetables, total = await timetable_crud.get_multi(db, filters=[timetable_crud.model.id == timetable_id], limit=1)
    if not timetables:
        raise HTTPException(status_code=404, detail="课表不存在")
    
    try:
        # 使用TimetableUpdate将is_delete设置为True来实现软删除
        delete_data = TimetableUpdate(is_delete=True)
        deleted_timetable = await timetable_crud.update(
            db, db_obj=timetables[0], obj_in=delete_data, exclude_unset=True
        )
        return BaseResponse(code=200, msg="success", data=TimetableResponse.model_validate(deleted_timetable))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除课表失败: {e}")


@router.get("/timetables", summary="获取课表列表")
async def list_timetables(
    teacher_id: Optional[int] = None,
    user_on: Optional[str] = None,
    college_id: Optional[int] = None,
    class_id: Optional[int] = None,
    class_name: Optional[str] = None,
    course_code: Optional[str] = None,
    course_name: Optional[str] = None,
    weekday: Optional[int] = None,
    period: Optional[str] = None,
    classroom: Optional[str] = None,
    academic_year: Optional[str] = None,
    semester: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: TokenData = Depends(
        # 22300417陈俫坤开发：督导老师需要查看负责范围内教师课表
        require_access(roles_any=("school_admin", "college_admin", "supervisor", "teacher"))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取课表列表，支持按教师、学院、班级、课程、时间等多维度过滤"""
    # 22300417陈俫坤开发：按角色限制数据范围
    # - teacher：仅允许看自己的课表
    # - supervisor/college_admin：仅允许看本学院课表
    # - school_admin：不限制
    roles = await get_roles_code(db, current_user)
    is_school_admin = "school_admin" in roles
    is_supervisor = "supervisor" in roles
    is_college_admin = "college_admin" in roles
    is_college_scope = is_college_admin or is_supervisor
    is_teacher_only = ("teacher" in roles) and (not is_school_admin) and (not is_college_scope)

    if is_teacher_only:
        # teacher 强制限定 teacher_id = 当前用户，并禁止通过 user_on/college_id 绕过
        teacher_id = current_user.id
        user_on = None
        college_id = None
    elif is_college_scope and not is_school_admin:
        # 22300417陈俫坤开发：范围限制
        # - college_admin：只能看本学院（固定）
        # - supervisor：优先按 supervisor_scope 配置；未配置时回退到 current_user.college_id
        if is_college_admin:
            if not getattr(current_user, "college_id", None):
                raise HTTPException(status_code=403, detail="未设置学院，无法查看学院课表")
            if college_id and int(college_id) != int(current_user.college_id):
                raise HTTPException(status_code=403, detail="无权查看其他学院课表")
            college_id = int(current_user.college_id)
        elif is_supervisor:
            allow_college_ids, allow_room_ids = await get_effective_supervisor_scope(db, current_user=current_user)
            if not allow_college_ids and not allow_room_ids:
                raise HTTPException(status_code=403, detail="未配置负责范围，且未设置学院")

            # 如果前端指定 college_id，必须在允许范围内（仅当配置了 college_ids 时校验）
            if college_id is not None and allow_college_ids:
                if int(college_id) not in [int(x) for x in allow_college_ids]:
                    raise HTTPException(status_code=403, detail="无权查看该学院课表")

    # 构建过滤条件
    filters = []
    if academic_year:
        filters.append(timetable_crud.model.academic_year == academic_year)
    if semester is not None:
        filters.append(timetable_crud.model.semester == semester)
    if teacher_id:
        filters.append(timetable_crud.model.teacher_id == teacher_id)
    if college_id:
        filters.append(timetable_crud.model.college_id == college_id)
    else:
        # 22300417陈俫坤开发：督导配置了多学院范围时，默认限定在这些学院
        if is_supervisor and (not is_school_admin):
            allow_college_ids, allow_room_ids = await get_effective_supervisor_scope(db, current_user=current_user)
            if allow_college_ids:
                filters.append(timetable_crud.model.college_id.in_(allow_college_ids))
    if class_id:
        filters.append(timetable_crud.model.class_id == class_id)
    if class_name:
        filters.append(timetable_crud.model.class_name.like(f"%{class_name}%"))
    if course_code:
        filters.append(timetable_crud.model.course_code == course_code)
    if course_name:
        filters.append(timetable_crud.model.course_name.like(f"%{course_name}%"))
    if weekday is not None:
        filters.append(timetable_crud.model.weekday == weekday)
    if period:
        filters.append(timetable_crud.model.period == period)
    if classroom:
        filters.append(timetable_crud.model.classroom.like(f"%{classroom}%"))
    
    # 如果提供了user_on，通过关联User表过滤
    if user_on:
        from sqlalchemy.orm import joinedload
        from app.models import User
        
        # 22300417陈俫坤开发：支持按教师工号/账号（User.user_on）查询课表。
        # 这里必须 join User，否则 where(User.user_on...) 无法正确关联到课表的 teacher_id。
        # 使用 joinedload 预加载 teacher 关系，避免后续序列化时额外查询。
        timetables = await db.execute(
            select(timetable_crud.model)
            .join(User, timetable_crud.model.teacher_id == User.id)
            .options(joinedload(timetable_crud.model.teacher))
            .where(
                *filters,
                User.user_on.like(f"%{user_on}%")
            )
            .offset(skip)
            .limit(limit)
            .order_by(timetable_crud.model.weekday, timetable_crud.model.period, timetable_crud.model.section_time)
        )
        timetables = timetables.scalars().all()
        
        # 计算总数
        total = await db.execute(
            select(func.count())
            .select_from(timetable_crud.model)
            .join(User, timetable_crud.model.teacher_id == User.id)
            .where(
                *filters,
                User.user_on.like(f"%{user_on}%")
            )
        )
        total = total.scalar_one()
    else:
        # 常规查询
        # 22300417陈俫坤开发：如果督导只配置了教研室范围（无 college_ids），则 join TeacherProfile 过滤 research_room_id
        if is_supervisor and (not is_school_admin):
            allow_college_ids, allow_room_ids = await get_effective_supervisor_scope(db, current_user=current_user)
            if (not allow_college_ids) and allow_room_ids:
                from app.models import TeacherProfile
                base_stmt = (
                    select(timetable_crud.model)
                    .join(TeacherProfile, TeacherProfile.user_id == timetable_crud.model.teacher_id)
                    .where(*filters, TeacherProfile.research_room_id.in_(allow_room_ids))
                    .offset(skip)
                    .limit(limit)
                    .order_by(timetable_crud.model.weekday, timetable_crud.model.period, timetable_crud.model.section_time)
                )
                res = await db.execute(base_stmt)
                timetables = res.scalars().all()
                total_res = await db.execute(
                    select(func.count())
                    .select_from(timetable_crud.model)
                    .join(TeacherProfile, TeacherProfile.user_id == timetable_crud.model.teacher_id)
                    .where(*filters, TeacherProfile.research_room_id.in_(allow_room_ids))
                )
                total = total_res.scalar_one()
            else:
                timetables, total = await timetable_crud.get_multi(
                    db,
                    filters=filters,
                    skip=skip,
                    limit=limit,
                    order_by=[timetable_crud.model.weekday, timetable_crud.model.period, timetable_crud.model.section_time],
                )
        else:
            timetables, total = await timetable_crud.get_multi(
                db,
                filters=filters,
                skip=skip,
                limit=limit,
                order_by=[timetable_crud.model.weekday, timetable_crud.model.period, timetable_crud.model.section_time],
            )
    
    # 转换为响应模型
    timetable_responses = [TimetableResponse.model_validate(timetable) for timetable in timetables]
    
    return BaseResponse(
        code=200,
        msg="success",
        data={
            "list": timetable_responses,
            "total": total,
            "skip": skip,
            "limit": limit,
        },
    )