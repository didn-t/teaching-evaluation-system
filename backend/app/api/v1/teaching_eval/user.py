from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy import select

from app.database import get_db
from app.schemas import UserBase, UserCreate, TokenData, BaseResponse, UserUpdate, SupervisorScopeUpdate, SupervisorScopeResponse
from app.crud.user import (
    get_user, create_user, update_user, get_roles_name, get_roles_code, 
    get_user_permissions, reset_user_password, get_user_role_level, get_users_list, get_user_by_id
)
from app.crud.user import get_supervisor_scope_ids, set_supervisor_scope_ids
from app.core import hash_password, create_access_token, verify_password
from app.core.deps import get_current_user, require_access
from app.models import Role, UserRole, College, TeacherProfile, ResearchRoom

router = APIRouter(prefix="", tags=["用户"])


def set_token_in_response(request: Request, user):
    token_obj = create_access_token(TokenData(
        id=user.id,
        user_on=user.user_on,
        college_id=user.college_id,
        status=user.status,
        is_delete=user.is_delete
    ))
    request.state.token_to_set = token_obj.token


async def user_payload_with_college(db: AsyncSession, user):
    """22300417陈俫坤开发：补齐 college_name，便于小程序个人信息页展示与编辑学院"""
    college_name = None
    research_room_id = None
    research_room_name = None
    try:
        if getattr(user, "college_id", None):
            college = await db.get(College, user.college_id)
            college_name = getattr(college, "college_name", None) if college else None
    except Exception:
        college_name = None

    try:
        res = await db.execute(
            select(TeacherProfile.research_room_id)
            .where(
                TeacherProfile.user_id == user.id,
                TeacherProfile.is_delete == False,  # noqa: E712
            )
            .limit(1)
        )
        research_room_id = res.scalar_one_or_none()
        if research_room_id:
            room = await db.get(ResearchRoom, research_room_id)
            research_room_name = getattr(room, "room_name", None) if room else None
    except Exception:
        research_room_id = None
        research_room_name = None

    return {
        "id": user.id,
        "user_on": user.user_on,
        "user_name": user.user_name,
        "college_id": user.college_id,
        "college_name": college_name,
        # 22300417陈俫坤开发：教师可同时属于学院与教研室
        "research_room_id": research_room_id,
        "research_room_name": research_room_name,
        "status": user.status,
    }


@router.get("/research-rooms", summary="教研室列表（个人资料选择）")
async def list_research_rooms_for_profile(
    college_id: Optional[int] = Query(None, description="学院ID（不传则默认当前用户学院）"),
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """22300417陈俫坤开发：个人资料编辑页使用的教研室下拉列表

    教师仅允许选择本学院教研室（默认用 current_user.college_id 过滤）。
    """
    cid = college_id
    if cid is None and getattr(current_user, "college_id", None):
        cid = int(current_user.college_id)

    stmt = select(ResearchRoom).where(ResearchRoom.is_delete == False)  # noqa: E712
    if cid is not None:
        stmt = stmt.where(ResearchRoom.college_id == cid)

    rows = list((await db.execute(stmt.order_by(ResearchRoom.id.asc()))).scalars().all())
    return BaseResponse(
        code=200,
        msg="success",
        data={
            "list": [
                {
                    "id": int(x.id),
                    "college_id": int(x.college_id),
                    "room_name": x.room_name,
                }
                for x in rows
            ]
        },
    )


@router.post("/register", summary="用户注册")
async def register(form: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    existing = await get_user(db, form.user_on)
    if existing:
        raise HTTPException(status_code=400, detail="用户已存在")

    user_data = {
        "user_on": form.user_on,
        "user_name": form.user_name,
        "password": form.password,  # 传递明文密码，由CRUD层处理哈希
        "college_id": form.college_id,
        "status": 1,
        "is_delete": False,
    }

    user = await create_user(db, user_data)
    if not user:
        raise HTTPException(status_code=500, detail="创建失败")

    # 22300417陈俫坤开发：注册后默认绑定 teacher 角色（如果存在），避免新用户无任何权限
    try:
        res = await db.execute(
            select(Role).where(Role.role_code == "teacher", Role.is_delete == False)  # noqa: E712
        )
        teacher_role = res.scalars().first()
        if teacher_role:
            # 复用 auth.py 的逻辑：删除旧关联再新增（注册用户理论上无旧关联）
            from app.models import UserRole

            db.add(UserRole(user_id=user.id, role_id=teacher_role.id))
            await db.commit()
    except Exception:
        await db.rollback()

    set_token_in_response(request, user)
    # 22300417陈俫坤开发：注册成功后直接返回角色/权限，便于前端立刻显示可用功能
    roles_name = await get_roles_name(db, TokenData(id=user.id, user_on=user.user_on, college_id=user.college_id, status=user.status, is_delete=user.is_delete))
    roles_code = await get_roles_code(db, TokenData(id=user.id, user_on=user.user_on, college_id=user.college_id, status=user.status, is_delete=user.is_delete))
    permissions = await get_user_permissions(db, TokenData(id=user.id, user_on=user.user_on, college_id=user.college_id, status=user.status, is_delete=user.is_delete))
    return BaseResponse(code=200, msg="success", data={
        "user": await user_payload_with_college(db, user),
        "roles_name": roles_name,
        "roles_code": roles_code,
        "permissions": permissions,
    })


@router.post("/login", summary="用户登录")
async def login(form: UserBase, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, form.user_on)
    print(form)
    if not user:
        raise HTTPException(status_code=400, detail="账号或密码错误")

    if not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="账号或密码错误")

    set_token_in_response(request, user)
    return BaseResponse(code=200, msg="success", data={"user": await user_payload_with_college(db, user)})


@router.get("/me", summary="我的信息（新增）")
async def me(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user(db, current_user.user_on)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    roles_name = await get_roles_name(db, current_user)
    roles_code = await get_roles_code(db, current_user)
    permissions = await get_user_permissions(db, current_user)

    return BaseResponse(code=200, msg="success", data={
        "user": await user_payload_with_college(db, user),
        "roles_name": roles_name,
        "roles_code": roles_code,
        "permissions": permissions,
    })


@router.patch("/update", summary="用户信息更新")
async def update_user_info(
    update_data: UserUpdate,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    new_user = await update_user(db, current_user, update_data)
    if not new_user:
        raise HTTPException(status_code=400, detail="更新失败")

    set_token_in_response(request, new_user)
    return BaseResponse(code=200, msg="success", data={"user": await user_payload_with_college(db, new_user)})


@router.post("/change-password", summary="修改密码（新增）")
async def change_password(
    old_password: str,
    new_password: str,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user(db, current_user.user_on)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if not verify_password(old_password, user.password):
        raise HTTPException(status_code=400, detail="旧密码不正确")

    user.password = hash_password(new_password)
    try:
        await db.commit()
        await db.refresh(user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"修改密码失败: {e}")

    set_token_in_response(request, user)  # 换新 token（可选）
    return BaseResponse(code=200, msg="success", data=None)


@router.post("/reset-password", summary="重置用户密码")
async def reset_password(
    user_id: int,
    new_password: str,
    current_user: TokenData = Depends(require_access(perms_any=["user:manage:college", "user:manage:all"])),
    db: AsyncSession = Depends(get_db),
):
    """
    重置用户密码
    - 学校管理员（role_level=4）：可重置所有用户密码
    - 学院管理员（role_level=3）：可重置督导老师（role_level=2）和老师（role_level=1）密码
    """
    # 获取当前用户角色等级
    current_role_level = await get_user_role_level(db, current_user)
    
    # 获取目标用户
    target_user = await get_user_by_id(db, TokenData(id=user_id, user_on="", college_id=None, status=1, is_delete=False))
    if not target_user:
        raise HTTPException(status_code=404, detail="目标用户不存在")
    
    # 获取目标用户角色等级
    target_role_level = await get_user_role_level(db, TokenData(id=user_id, user_on="", college_id=None, status=1, is_delete=False))
    
    # 权限检查
    # 学校管理员（role_level=4）可以重置所有用户
    # 学院管理员（role_level=3）只能重置督导老师（role_level=2）和老师（role_level=1）
    if current_role_level == 4:  # 学校管理员
        pass  # 可以重置所有用户
    elif current_role_level == 3:  # 学院管理员
        if target_role_level < 3:  # 只能重置角色等级小于3的用户
            pass
        else:
            raise HTTPException(status_code=403, detail="没有权限重置该用户密码")
    else:
        raise HTTPException(status_code=403, detail="没有权限执行此操作")
    
    # 执行密码重置
    updated_user = await reset_user_password(db, user_id=user_id, new_password=new_password)
    if not updated_user:
        raise HTTPException(status_code=500, detail="密码重置失败")
    
    return BaseResponse(code=200, msg="密码重置成功", data=None)


@router.get("/list", summary="分页获取用户列表")
async def get_users(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(20, ge=1, le=100, description="每页条数"),
    college_id: Optional[int] = Query(None, description="学院ID"),
    current_user: TokenData = Depends(require_access(perms_any=["user:manage:college", "user:manage:all"])),
    db: AsyncSession = Depends(get_db),
):
    """
    分页获取用户列表
    - 学校管理员（role_level=4）：可查看所有用户
    - 学院管理员（role_level=3）：可查看本院督导老师和老师
    - 按角色等级和学院获取对应角色的列表
    """
    # 获取当前用户角色等级
    current_role_level = await get_user_role_level(db, current_user)
    
    # 获取当前用户学院ID
    current_user_obj = await get_user_by_id(db, current_user)
    current_college_id = current_user_obj.college_id if current_user_obj else None
    
    # 确定查询参数
    query_college_id = None
    max_role_level = None
    
    # 权限检查和参数设置
    if current_role_level == 4:  # 学校管理员
        # 可以查看所有用户，不限制学院和角色等级
        query_college_id = college_id  # 支持按学院过滤
        max_role_level = 4  # 可以查看所有角色等级
    elif current_role_level == 3:  # 学院管理员
        # 只能查看本院的用户
        query_college_id = current_college_id
        # 只能查看角色等级小于3的用户（督导老师和老师）
        max_role_level = 2
    else:
        raise HTTPException(status_code=403, detail="没有权限执行此操作")
    
    # 查询用户列表
    users, total = await get_users_list(
        db, 
        skip=skip, 
        limit=limit, 
        college_id=query_college_id, 
        max_role_level=max_role_level
    )
    
    # 构造响应数据
    user_list = []
    for user in users:
        # 获取用户角色
        # 22300417陈俫坤开发：同时返回 role_ids/role_codes，便于前端回显并准确分配角色
        token_stub = TokenData(id=user.id, user_on="", college_id=None, status=1, is_delete=False)
        user_roles = await get_roles_name(db, token_stub)
        user_role_codes = await get_roles_code(db, token_stub)
        role_ids_stmt = select(UserRole.role_id).where(UserRole.user_id == user.id)
        role_ids_res = await db.execute(role_ids_stmt)
        user_role_ids = list(role_ids_res.scalars().all())
        user_list.append({
            "id": user.id,
            "user_on": user.user_on,
            "user_name": user.user_name,
            "college_id": user.college_id,
            "status": user.status,
            "roles": user_roles,
            "role_codes": user_role_codes,
            "role_ids": user_role_ids
        })
    
    return BaseResponse(
        code=200, 
        msg="success", 
        data={
            "items": user_list,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/supervisor/{supervisor_user_id}/scope", summary="获取督导负责范围（学校管理员）")
async def get_supervisor_scope(
    supervisor_user_id: int,
    current_user: TokenData = Depends(require_access(roles_any=("school_admin",), perms_all=("user:manage:all",))),
    db: AsyncSession = Depends(get_db),
):
    """22300417陈俫坤开发：督导范围查询"""
    college_ids, research_room_ids = await get_supervisor_scope_ids(db, supervisor_user_id=supervisor_user_id)
    return BaseResponse(code=200, msg="success", data=SupervisorScopeResponse(
        supervisor_user_id=supervisor_user_id,
        college_ids=college_ids,
        research_room_ids=research_room_ids,
    ))


@router.put("/supervisor/{supervisor_user_id}/scope", summary="设置督导负责范围（学校管理员）")
async def set_supervisor_scope(
    supervisor_user_id: int,
    payload: SupervisorScopeUpdate,
    current_user: TokenData = Depends(require_access(roles_any=("school_admin",), perms_all=("user:manage:all",))),
    db: AsyncSession = Depends(get_db),
):
    """22300417陈俫坤开发：督导范围配置

    - 支持配置多学院 + 多教研室
    - 采用“软删旧记录 + 插入新记录”的幂等方式
    """
    # 校验目标用户存在
    target = await get_user_by_id(db, TokenData(id=supervisor_user_id, user_on="", college_id=None, status=1, is_delete=False))
    if not target:
        raise HTTPException(status_code=404, detail="目标用户不存在")

    await set_supervisor_scope_ids(
        db,
        supervisor_user_id=supervisor_user_id,
        college_ids=list(payload.college_ids or []),
        research_room_ids=list(payload.research_room_ids or []),
    )
    return BaseResponse(code=200, msg="success", data=None)
