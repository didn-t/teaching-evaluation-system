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
from app.crud.org import (
    college_crud,
    research_room_crud,
    major_crud,
    clazz_crud,
)
from app.crud.timetable import timetable_crud

router = APIRouter(prefix="/org", tags=["组织结构管理"])


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
        require_access(roles_any=("school_admin", "college_admin", "teacher"), perms_all=("org:college:read",))
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
        require_access(roles_any=("school_admin", "college_admin", "teacher"), perms_all=("org:college:read",))
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
        require_access(roles_any=("school_admin", "college_admin", "teacher"))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取课表列表，支持按教师、学院、班级、课程、时间等多维度过滤"""
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
        
        # 使用joinedload预加载teacher关系
        timetables = await db.execute(
            select(timetable_crud.model)
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