from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

from app.models import User
from app.schemas import Token, TokenData, UserCreate, UserResponse

# 加载环境变量
load_dotenv()

router = APIRouter()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 密码Bearer模式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# 验证密码
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 获取密码哈希
def get_password_hash(password):
    return pwd_context.hash(password)

# 根据用户名获取用户
async def get_user(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    try:
        return result.scalar_one()
    except NoResultFound:
        return None

# 验证用户
def authenticate_user(user: User, password: str):
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user



# 获取当前用户信息
@router.get("/me", response_model=UserResponse)
async def read_users_me():
    return "success"