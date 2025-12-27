from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import UserBase, UserCreate, TokenData, BaseResponse, UserUpdate
from app.crud.teaching_eval import create_user, get_user, get_roles_name, get_user_permissions, get_role_permissions, \
    update_user, get_roles_code
from app.core import hash_password, create_access_token, verify_password
from app.core.deps import get_current_user

router = APIRouter()


def set_token_in_response(request: Request, user):
    """
    在响应中设置token
    :param request: 请求对象
    :param user: 用户对象
    """
    token_obj = create_access_token(TokenData(
        id=user.id,
        user_on=user.user_on,
        college_id=user.college_id,
        status=user.status,
        is_delete=user.is_delete
    ))
    request.state.token_to_set = token_obj.token


def create_user_response(user):
    """
    创建用户响应
    :param user: 用户对象
    :return: BaseResponse
    """
    return BaseResponse(
        code=200,
        msg="success",
        data={
            "user": {
                "user_on": user.user_on,
                "user_name": user.user_name,
                "college_id": user.college_id,
            }
        },
    )


# 用户注册 - 公开路由，无需认证
@router.post("/register", summary="用户注册")
async def register(form: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    user = await get_user(db, form.user_on)
    if user:
        raise HTTPException(status_code=400, detail="用户已存在")

    user_data = {
        "user_on": form.user_on,
        "user_name": form.user_name,
        "password": hash_password(form.password),
        "college_id": form.college_id,
    }

    user = await create_user(db, user_data)
    if not user:
        raise HTTPException(status_code=500, detail="创建失败")

    set_token_in_response(request, user)
    return create_user_response(user)


# 用户登录 - 公开路由，无需认证
@router.post("/login", summary="用户登录")
async def login(form: UserBase, request: Request, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    user = await get_user(db, form.user_on)
    if not user:
        raise HTTPException(status_code=400, detail="账号或密码错误")

    if not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="账号或密码错误")

    set_token_in_response(request, user)
    return create_user_response(user)


@router.get("/role", summary="用户角色信息")
async def get_role(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户角色信息"""
    role_name_list = await get_roles_name(db, current_user)
    role_code_list = await get_roles_code(db, current_user)
    return BaseResponse(
        code=200,
        msg="success",
        data={
            "roles_name": role_name_list,
            "role_code" : role_code_list
        },
    )


@router.patch("/update", summary="用户信息更新")
async def update_user_info(
    update_data: UserUpdate,
    request: Request,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """用户信息更新"""
    new_user = await update_user(db, current_user, update_data)
    if not new_user:
        raise HTTPException(status_code=400, detail="更新失败")

    set_token_in_response(request, new_user)
    return create_user_response(new_user)


# @router.post("/logout", summary="用户登出")
# async def logout(current_user: TokenData = Depends(get_current_user)):
#     """用户登出"""
#     return BaseResponse(
#         code=200,
#         msg="success",
#         data=None,
#     )


@router.get("/role-permissions", summary="获取用户角色权限信息")
async def role_permissions(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取角色权限信息"""
    role = await get_roles_name(db, current_user)
    permissions = await get_role_permissions(db, current_user)

    return BaseResponse(
        code=200,
        msg="success",
        data={
            "role": role,
            "permissions": permissions,
        },
    )


@router.get("/permissions", summary="获取用户权限信息")
async def get_permissions(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户权限信息"""
    permissions = await get_user_permissions(db, current_user)
    return BaseResponse(
        code=200,
        msg="success",
        data={
            "permissions": permissions,
        }
    )
