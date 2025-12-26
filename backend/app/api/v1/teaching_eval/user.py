from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import UserBase, UserCreate, TokenData, BaseResponse, UserUpdate
from app.crud.teaching_eval import create_user, get_user, get_roles_name, get_user_permissions, get_role_permissions, \
    update_user
from app.core import hash_password, create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, verify_token

router = APIRouter()


def return_token_info(user):
    """
    创建token，并格式返回给前端
    :param user:
    :return:
    """
    token_payload = {
        "id": user.id,
        "user_on": user.user_on,
        "college_id": user.college_id,
        "status": user.status,
        "is_delete": user.is_delete,
    }
    token_data = TokenData(**token_payload)
    return BaseResponse(
        code=200,
        msg="success",
        # 合并字典 | 操作符（Python 3.9+）
        data=create_access_token(token_data).model_dump() | {
            "user": {
                "user_on": user.user_on,
                "user_name": user.user_name,
                "college_id": user.college_id,
            }
        },
    )


# 用户注册
@router.post("/register", summary="用户注册")
async def register(form: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, form.user_on)
    if user:
        return BaseResponse(
            code=400,
            msg="用户已存在",
            data=None,
        )


    user_data = {
        "user_on": form.user_on,
        "user_name": form.user_name,
        "password": hash_password(form.password),  # 哈希密码
        "college_id": form.college_id,
    }

    user = await create_user(db, user_data)
    if not user:
        return BaseResponse(
            code=500,
            msg="创建失败",
            data=None,
        )
    # 生成 Token,并返回
    return return_token_info(user)



@router.post("/login", summary="用户登录")
async def login(form: UserBase, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    print("form:", form)

    user = await get_user(db, form.user_on)
    if not user:
        return BaseResponse(
            code=400,
            msg="用户不存在",
            data=None,
        )

    # 校验密码
    if not verify_password(form.password, user.password):
        return BaseResponse(
            code=401,
            msg="账号或密码错误",
            data=None,
        )

    # 生成 Token,并返回
    return return_token_info(user)


@router.get("/role", summary="用户角色信息")
async def get_user_info(token_data: TokenData = Depends(verify_token), db: AsyncSession = Depends(get_db)):
    """获取用户角色信息"""

    if not token_data:
        return BaseResponse(
            code=401,
            msg="Token验证失败",
            data=None,
        )

    role_list = await get_roles_name(db, token_data)
    return BaseResponse(
        code=200,
        msg="success",
        data=create_access_token(token_data).model_dump() | {
            "user_on": token_data.user_on,
            "roles": role_list,
        },
    )



@router.patch("/update", summary="用户信息更新")
async def update_user_info(update_data: UserUpdate, token_data: TokenData = Depends(verify_token),
                           db: AsyncSession = Depends(get_db)):
    """用户信息更新"""
    if not token_data:
        return BaseResponse(
            code=401,
            msg="Token验证失败",
            data=None,
        )

    try:
        new_user = await update_user(db, token_data, update_data)
        if not new_user:
            return BaseResponse(
                code=400,
                msg="fail",
                data=None,
            )
    except Exception as e:
        print(e)
        return BaseResponse(
            code=500,
            msg="服务器错误",
            data=None,
        )

    return return_token_info(new_user)


# 示例 解析token
@router.post("/logout", summary="用户登出")
async def logout(token_data: TokenData = Depends(verify_token)):  # 调用verify_token方法返回一个TokenData对象
    """用户登出"""
    if not token_data:
        raise HTTPException(status_code=401, detail="Token验证失败")
    return BaseResponse(
        code=200,
        msg="success",
        data=None,
    )


@router.get("/role-permissions", summary="获取用户信息")
async def role_permissions(token_data: TokenData = Depends(verify_token), db: AsyncSession = Depends(get_db)):
    """获取用户角色权限信息"""
    if not token_data:
        return BaseResponse(
            code=401,
            msg="Token验证失败",
            data=create_access_token(token_data),
        )
    try:
        role_list = await get_roles_name(db, token_data)
        permissions = await get_role_permissions(db, token_data)

        token = create_access_token(token_data)
        return BaseResponse(
            code=200,
            msg="success",
            data=token.model_dump() | {
                "user_on": token_data.user_on,
                "roles": role_list,
                "permissions": permissions,
            },
        )
    except Exception as e:
        print(e)
        return BaseResponse(
            code=500,
            msg="服务器错误",
            data=None,
        )


@router.get("/permissions", summary="获取用户权限信息")
async def get_user_info(token_data: TokenData = Depends(verify_token), db: AsyncSession = Depends(get_db)):
    """获取用户信息"""

    if not token_data:
        return BaseResponse(
            code=401,
            msg="Token验证失败",
            data=None,
        )
    try:
        permissions = await get_user_permissions(db, token_data)
        return BaseResponse(
            code=200,
            msg="success",
            data=create_access_token(token_data).model_dump() | {
                "user_on": token_data.user_on,
                "permissions": permissions,
            }
        )
    except Exception as e:
        print(e)
        return BaseResponse(
            code=500,
            msg="服务器错误",
            data=None,
        )
