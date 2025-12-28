from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import UserBase, UserCreate, TokenData, BaseResponse, UserUpdate
from app.crud.user import get_user, create_user, update_user, get_roles_name, get_roles_code, get_user_permissions
from app.core import hash_password, create_access_token, verify_password
from app.core.deps import get_current_user

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
        print(111111)
        raise HTTPException(status_code=400, detail="账号或密码错误")

    if not verify_password(form.password, user.password):
        print(222222)
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
