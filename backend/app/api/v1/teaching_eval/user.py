import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.schemas import Token, TokenData, LoginForm
from pathlib import Path

project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path, encoding='utf-8')

router = APIRouter()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 返回token，过期时间
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire


# 用户登录
@router.post("/login")
async def login(form: LoginForm, db: AsyncSession = Depends(get_db)):
    # 查询用户
    user = await User.get_by_user_no(db, form.user_no)
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
        "user_no": user.user_no,
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
                "user_no": user.user_no,
                "user_name": user.user_name,
                "role_type": user.role_type,
                "college_id": user.college_id,
            }
        },
        "timestamp": datetime.now().timestamp(),
    }


@router.get("/info")
async def login(a: int = 0, b: int = 10):
    return {"a": a, "b": b}
