from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas import UserBase, UserCreate, TokenData, BaseResponse, UserUpdate
from app.crud.user import (
    get_user, create_user, update_user, get_roles_name, get_roles_code, 
    get_user_permissions, reset_user_password, get_user_role_level, get_users_list
)
from app.core import hash_password, create_access_token, verify_password
from app.core.deps import get_current_user, require_access

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


def user_payload(user):
    return {
        "id": user.id,
        "user_on": user.user_on,
        "user_name": user.user_name,
        "college_id": user.college_id,
        "status": user.status,
    }


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

    set_token_in_response(request, user)
    return BaseResponse(code=200, msg="success", data={"user": user_payload(user)})


@router.post("/login", summary="用户登录")
async def login(form: UserBase, request: Request, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, form.user_on)
    print(form)
    if not user:
        raise HTTPException(status_code=400, detail="账号或密码错误")

    if not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="账号或密码错误")

    set_token_in_response(request, user)
    return BaseResponse(code=200, msg="success", data={"user": user_payload(user)})


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
        "user": user_payload(user),
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
    return BaseResponse(code=200, msg="success", data={"user": user_payload(new_user)})


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
        user_roles = await get_roles_name(db, TokenData(id=user.id, user_on="", college_id=None, status=1, is_delete=False))
        user_list.append({
            "id": user.id,
            "user_on": user.user_on,
            "user_name": user.user_name,
            "college_id": user.college_id,
            "status": user.status,
            "roles": user_roles
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
