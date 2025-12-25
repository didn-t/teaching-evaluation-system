import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from dotenv import load_dotenv
from jose import jwt
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import Token, TokenData, LoginForm, UserCreate
from pathlib import Path
from app.crud.teaching_eval import create_user, get_user_by_user_id

project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path, encoding='utf-8')

router = APIRouter()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')


def hash_password(password: str) -> str:
    # 密码需要编码为 bytes，且不能超过 72 字节
    password_bytes = password.encode('utf-8')[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# 返回token，过期时间
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire


# 用户注册
@router.post("/register")
async def register(form: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_user_id(db, form.user_id)
    if user:
        return {
            "code": 400,
            "msg": "用户已存在",
            "data": None,
            "timestamp": datetime.now().timestamp(),
        }
    try:
        user_data = {
            "user_id": form.user_id,
            "user_name": form.user_name,
            "password": hash_password(form.password),  # 哈希密码
            "college_id": form.college_id,
        }

        user = await create_user(db, user_data)

        # 生成 Token
        token_payload = {
            "user_id": user.id,
            "user_id": user.user_id,
            "role_type": user.role_type,
            "college_id": user.college_id,
        }
        access_token, expire_time = create_access_token(
            data=token_payload,
            expires_delta=timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
        )

        return {
            "code": 200,
            "msg": "注册成功",
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "expire_time": expire_time,
                "user": {
                    "id": user.id,
                    "user_id": user.user_id,
                    "user_name": user.user_name,
                    "role_type": user.role_type,
                    "college_id": user.college_id,
                }
            },
            "timestamp": datetime.now().timestamp(),
        }
    except Exception as e:
        print(e)
        # <CHANGE> 返回更详细的错误信息
        error_msg = str(e)
        if "cannot be null" in error_msg:
            return {
                "code": 400,
                "msg": "缺少必填字段：role_type",
                "data": None,
                "timestamp": datetime.now().timestamp(),
            }
        return {
            "code": 500,
            "msg": "服务器错误",
            "data": None,
            "timestamp": datetime.now().timestamp(),
        }


# 用户登录
@router.post("/login")
async def login(form: LoginForm, db: AsyncSession = Depends(get_db)):
    # 查询用户
    user = await get_user_by_user_id(db, form.user_id)
    if not user:
        return {
            "code": 401,
            "msg": "账号或密码错误",
            "data": None,
            "timestamp": datetime.now().timestamp(),
        }

    # 校验密码
    if not verify_password(form.password, user.password):
        return {
            "code": 401,
            "msg": "账号或密码错误",
            "data": None,
            "timestamp": datetime.now().timestamp(),
        }

    # 生成 Token
    token_payload = {
        "user_id": user.id,
        "user_id": user.user_id,
        "role_type": user.role_type,
        "college_id": user.college_id,
    }

    access_token, expire_time = create_access_token(
        data=token_payload,
        expires_delta=timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    )

    # 返回
    return {
        "code": 200,
        "msg": "登录成功",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expire_time": expire_time,
            "user": {
                "id": user.id,
                "user_id": user.user_id,
                "user_name": user.user_name,
                "role_type": user.role_type,
                "college_id": user.college_id,
            }
        },
        "timestamp": datetime.now().timestamp(),
    }
